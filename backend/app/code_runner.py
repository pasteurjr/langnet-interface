"""
Subprocess runner para o sistema agêntico gerado, usando o ambiente conda
``langnet`` (compartilhado entre runs).

Pipeline ao iniciar um run:
1. Cria /tmp/langnet-runs/<session_id>/<run_id>/
2. Escreve arquivos da sessão lá dentro
3. Valida que o env conda ``langnet`` existe
4. Checa deps faltantes (pip dry-run) e instala APENAS o que falta NO env langnet
5. Sobe ``conda env python main.py`` em background
6. Stream stdout/stderr para buffer em memória + asyncio.Queue (consumido pelo WS)

Não cria venv local — usa /home/pasteurjr/miniconda3/envs/langnet/bin/python.

Cada run mantém: status (preparing|installing|running|stopped|crashed),
exit_code, stdout (lista de linhas), processo Popen, queue de novas linhas
para WS subscribers.
"""

from __future__ import annotations

import asyncio
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


RUNS_ROOT = Path(os.environ.get("LANGNET_RUNS_ROOT", "/tmp/langnet-runs"))
PIP_TIMEOUT_SECONDS = 600  # 10 min para instalar deps faltantes
MAX_STDOUT_LINES = 5000     # buffer cap (linhas anteriores ficam — só limita memória)

# Localiza o conda env "langnet". Se LANGNET_CONDA_ENV apontar para outro path, respeita.
CONDA_ENV_PATH = Path(os.environ.get(
    "LANGNET_CONDA_ENV",
    "/home/pasteurjr/miniconda3/envs/langnet",
))


def _conda_bin(name: str) -> Path:
    """Retorna o caminho de um binário dentro do env conda (python, pip)."""
    sub = "Scripts" if os.name == "nt" else "bin"
    suffix = ".exe" if os.name == "nt" else ""
    return CONDA_ENV_PATH / sub / f"{name}{suffix}"


def env_exists() -> bool:
    return _conda_bin("python").exists()


@dataclass
class CodeRun:
    """Estado de uma execução subprocess do código gerado."""
    id: str
    session_id: str
    work_dir: Path
    status: str = "preparing"           # preparing | installing | running | stopped | crashed
    started_at: str = ""
    finished_at: str = ""
    exit_code: Optional[int] = None
    process: Optional[subprocess.Popen] = None
    stdout_lines: List[str] = field(default_factory=list)
    _subscribers: List[asyncio.Queue] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _main_loop: Optional[asyncio.AbstractEventLoop] = None

    def to_public(self) -> Dict[str, Any]:
        return {
            "run_id": self.id,
            "session_id": self.session_id,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "exit_code": self.exit_code,
            "work_dir": str(self.work_dir),
            "total_lines": len(self.stdout_lines),
        }

    def append_line(self, line: str) -> None:
        """Append + broadcast para subscribers do WS (thread-safe)."""
        with self._lock:
            self.stdout_lines.append(line)
            if len(self.stdout_lines) > MAX_STDOUT_LINES:
                # Drop oldest, mantém os últimos MAX_STDOUT_LINES
                drop = len(self.stdout_lines) - MAX_STDOUT_LINES
                self.stdout_lines = self.stdout_lines[drop:]
            subs = list(self._subscribers)
        loop = self._main_loop
        if loop is None:
            return
        for q in subs:
            try:
                loop.call_soon_threadsafe(q.put_nowait, {"type": "line", "data": line})
            except Exception:
                pass

    def broadcast_status(self) -> None:
        """Avisa subscribers de mudança de status."""
        loop = self._main_loop
        if loop is None:
            return
        with self._lock:
            subs = list(self._subscribers)
        for q in subs:
            try:
                loop.call_soon_threadsafe(q.put_nowait, {"type": "status", "data": self.to_public()})
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# Registry global em memória (não precisa persistir — runs são efêmeros)
# ─────────────────────────────────────────────────────────────────────────────

_RUNS: Dict[str, CodeRun] = {}
_RUNS_LOCK = threading.Lock()


def get_run(run_id: str) -> Optional[CodeRun]:
    return _RUNS.get(run_id)


def list_runs_for_session(session_id: str) -> List[CodeRun]:
    return [r for r in _RUNS.values() if r.session_id == session_id]


def _safe_write_files(work_dir: Path, files: List[Dict[str, Any]]) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        path = work_dir / Path(f["path"]).as_posix().lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f.get("content", "")
        if not isinstance(content, str):
            import json as _json
            content = _json.dumps(content, ensure_ascii=False, indent=2)
        path.write_text(content, encoding="utf-8")


def _stream_pipe(run: CodeRun, pipe, prefix: str = "") -> None:
    """Lê linha-a-linha de um pipe (stdout/stderr) e despacha pra run."""
    try:
        for raw in iter(pipe.readline, b""):
            try:
                line = raw.decode("utf-8", errors="replace").rstrip("\n")
            except Exception:
                line = repr(raw)
            run.append_line(f"{prefix}{line}")
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def _check_missing_deps(req_file: Path, run: CodeRun) -> List[str]:
    """Roda `pip install --dry-run -r requirements.txt` no env langnet e
    retorna a lista de pacotes que SERIAM instalados (vazio = todos OK)."""
    if not req_file.exists():
        return []
    pip = _conda_bin("pip")
    try:
        # --dry-run + --quiet imprime "Would install pkg-x.y.z" para cada faltante
        proc = subprocess.run(
            [str(pip), "install", "--dry-run", "--no-deps", "-r", str(req_file)],
            cwd=str(run.work_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = (proc.stdout or "") + (proc.stderr or "")
        missing: List[str] = []
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Would install"):
                # "Would install pkg-1.2 pkg-3.4 ..."
                tokens = line.removeprefix("Would install").strip().split()
                missing.extend(tokens)
        return missing
    except Exception as exc:  # noqa: BLE001
        run.append_line(f"[runner] WARN: pip dry-run falhou ({exc}); assumindo deps OK")
        return []


def _install_missing(req_file: Path, run: CodeRun) -> bool:
    """Instala deps faltantes NO env langnet (não cria venv local)."""
    pip = _conda_bin("pip")
    run.append_line(f"[runner] pip install --upgrade -r requirements.txt (env=langnet)")
    try:
        proc = subprocess.Popen(
            [str(pip), "install", "--no-cache-dir", "-r", str(req_file)],
            cwd=str(run.work_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
            run.append_line(f"[pip] {line}")
        proc.wait(timeout=PIP_TIMEOUT_SECONDS)
        if proc.returncode != 0:
            run.append_line(f"[runner] pip install FAILED (exit {proc.returncode})")
            return False
        return True
    except subprocess.TimeoutExpired:
        run.append_line("[runner] pip install TIMEOUT")
        return False


def _load_env_file_into(env: dict, path: Path) -> None:
    """Carrega KEY=VALUE de um .env para o dict env. Ignora se arquivo não existe."""
    if not path.exists():
        return
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            # Não sobrescreve quem já tinha (priority: existing env > file)
            if k and k not in env:
                env[k] = v
    except Exception:
        pass


def _run_backend_service(run: "CodeRun", backend_dir: Path, parent_env: dict, side_procs: list) -> None:
    """Sobe o backend FastAPI do pacote visualtasksexec.

    Usa o python do env conda langnet (já tem fastapi+uvicorn instalados).
    Stream com prefixo [backend].
    """
    try:
        env = parent_env.copy()
        env_python = _conda_bin("python")
        if not env_python.exists():
            run.append_line("[backend] env conda 'langnet' indisponível — pulando")
            return
        # FastAPI/uvicorn já existem no env langnet (usados pelo próprio LangNet)
        run.append_line(f"[backend] starting: {env_python} main.py (cwd={backend_dir})")
        proc = subprocess.Popen(
            [str(env_python), "main.py"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=1,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        side_procs.append(proc)
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
            run.append_line(f"[backend] {line}")
        try:
            proc.stdout.close()
        except Exception:
            pass
        rc = proc.wait()
        run.append_line(f"[backend] exited (code={rc})")
    except Exception as exc:  # noqa: BLE001
        run.append_line(f"[backend] ERROR: {exc}")


# Cache global de node_modules — instala uma vez, reusa em todos os runs
_FRONTEND_CACHE_DIR = Path(os.environ.get(
    "LANGNET_FRONTEND_CACHE",
    str(Path.home() / ".langnet-cache" / "frontend"),
))


def _ensure_frontend_cache(run: "CodeRun", template_pkg_json: str, npm_bin: Path, env: dict) -> bool:
    """Garante que ~/.langnet-cache/frontend/node_modules existe.

    Se package.json mudou desde a última instalação, reinstala.
    Retorna True se cache tá pronto.
    """
    cache_node_modules = _FRONTEND_CACHE_DIR / "node_modules"
    cache_pkg_json = _FRONTEND_CACHE_DIR / "package.json"

    _FRONTEND_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Invalida cache se package.json mudou
    same_pkg = cache_pkg_json.exists() and cache_pkg_json.read_text(encoding="utf-8").strip() == template_pkg_json.strip()
    if cache_node_modules.exists() and same_pkg:
        return True

    # Reconstrói o cache
    run.append_line(f"[frontend:cache] populando cache em {_FRONTEND_CACHE_DIR}")
    if cache_node_modules.exists():
        run.append_line("[frontend:cache] invalidando cache antigo (package.json mudou)")
        shutil.rmtree(cache_node_modules, ignore_errors=True)
    cache_pkg_json.write_text(template_pkg_json, encoding="utf-8")

    try:
        inst = subprocess.Popen(
            [str(npm_bin), "install", "--legacy-peer-deps", "--silent", "--no-audit", "--no-fund"],
            cwd=str(_FRONTEND_CACHE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=1,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        for raw in iter(inst.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
            if line and not line.startswith("npm WARN"):
                run.append_line(f"[frontend:cache] {line[:200]}")
        try:
            inst.stdout.close()
        except Exception:
            pass
        rc = inst.wait()
        if rc != 0:
            run.append_line(f"[frontend:cache] FALHOU (code={rc})")
            return False
    except Exception as exc:
        run.append_line(f"[frontend:cache] ERROR: {exc}")
        return False

    run.append_line("[frontend:cache] cache pronto ✓")
    return True


def _link_cache_into(frontend_dir: Path, run: "CodeRun") -> bool:
    """Faz hardlink (cp -al) do cache de node_modules para o frontend do run."""
    cache_nm = _FRONTEND_CACHE_DIR / "node_modules"
    dst_nm = frontend_dir / "node_modules"
    if dst_nm.exists():
        return True  # já tem node_modules local — não toca
    if not cache_nm.exists():
        return False
    try:
        # cp -al: hardlink recursivo. Instantâneo + zero disk extra.
        rc = subprocess.run(
            ["cp", "-al", str(cache_nm), str(dst_nm)],
            check=False,
            capture_output=True,
            text=True,
        ).returncode
        if rc == 0:
            run.append_line(f"[frontend:cache] hardlinked node_modules ({rc}) — pulando npm install")
            return True
        run.append_line(f"[frontend:cache] cp -al falhou (rc={rc}) — fallback para npm install")
        return False
    except Exception as exc:
        run.append_line(f"[frontend:cache] hardlink ERROR: {exc} — fallback para npm install")
        return False


def _find_node_bin() -> Optional[Path]:
    """Localiza um node disponível (NVM, /usr/local/bin, etc)."""
    candidates: List[Path] = []
    if shutil.which("node"):
        candidates.append(Path(shutil.which("node")))
    nvm = Path.home() / ".nvm/versions/node"
    if nvm.exists():
        # Pega a versão mais recente
        versions = sorted((p for p in nvm.iterdir() if p.is_dir()), reverse=True)
        for v in versions:
            cand = v / "bin/node"
            if cand.exists():
                candidates.append(cand)
                break
    for c in candidates:
        if c.exists():
            return c
    return None


def _run_frontend_service(run: "CodeRun", frontend_dir: Path, parent_env: dict, side_procs: list) -> None:
    """Sobe o frontend React (npm install se preciso + npm start).

    Pode demorar 1-2min na primeira vez (install). Stream com prefixo [frontend].
    """
    try:
        node_bin = _find_node_bin()
        if not node_bin:
            run.append_line("[frontend] node não encontrado no PATH — instale Node.js ou NVM")
            return
        npm_bin = node_bin.parent / "npm"
        if not npm_bin.exists():
            run.append_line(f"[frontend] npm não encontrado em {npm_bin}")
            return

        env = parent_env.copy()
        # Garante PATH com node bin
        env["PATH"] = f"{node_bin.parent}:{env.get('PATH','')}"
        env["BROWSER"] = "none"  # não tenta abrir browser

        # 1) Garante node_modules: usa cache global (hardlink) se possível.
        if not (frontend_dir / "node_modules").exists():
            pkg_json_text = (frontend_dir / "package.json").read_text(encoding="utf-8") if (frontend_dir / "package.json").exists() else ""
            # 1a) Popula cache se ainda não existe (ou se package.json mudou)
            cache_ok = _ensure_frontend_cache(run, pkg_json_text, npm_bin, env)
            # 1b) Hardlink cache → node_modules do run (instantâneo)
            linked = cache_ok and _link_cache_into(frontend_dir, run)
            if not linked:
                run.append_line("[frontend] sem cache — npm install local (1-2 min)...")
                inst = subprocess.Popen(
                    [str(npm_bin), "install", "--legacy-peer-deps", "--silent", "--no-audit", "--no-fund"],
                    cwd=str(frontend_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=env,
                    bufsize=1,
                    preexec_fn=os.setsid if os.name != "nt" else None,
                )
                side_procs.append(inst)
                for raw in iter(inst.stdout.readline, b""):
                    line = raw.decode("utf-8", errors="replace").rstrip("\n")
                    if line and not line.startswith("npm WARN"):
                        run.append_line(f"[frontend:install] {line[:200]}")
                try:
                    inst.stdout.close()
                except Exception:
                    pass
                rc = inst.wait()
                if rc != 0:
                    run.append_line(f"[frontend] npm install FALHOU (code={rc})")
                    return
                run.append_line("[frontend] npm install OK")
                try:
                    side_procs.remove(inst)
                except ValueError:
                    pass

        # 2) npm start
        run.append_line(f"[frontend] starting: {npm_bin} start (cwd={frontend_dir})")
        proc = subprocess.Popen(
            [str(npm_bin), "start"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=1,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        side_procs.append(proc)
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
            if line:
                run.append_line(f"[frontend] {line[:300]}")
        try:
            proc.stdout.close()
        except Exception:
            pass
        rc = proc.wait()
        run.append_line(f"[frontend] exited (code={rc})")
    except Exception as exc:  # noqa: BLE001
        run.append_line(f"[frontend] ERROR: {exc}")


def _worker(run: CodeRun, files: List[Dict[str, Any]]) -> None:
    """Thread worker: usa env conda langnet, instala apenas o que falta, sobe main.py."""
    try:
        # 0) Verifica env conda
        if not env_exists():
            run.status = "crashed"
            run.append_line(
                f"[runner] env conda 'langnet' NÃO encontrado em {CONDA_ENV_PATH}. "
                f"Crie com: conda create -n langnet python=3.11 && conda activate langnet && "
                f"pip install crewai langchain websockets pyyaml python-dotenv"
            )
            run.broadcast_status()
            return

        # 1) Escreve arquivos
        run.append_line(f"[runner] writing {len(files)} file(s) to {run.work_dir}")
        _safe_write_files(run.work_dir, files)

        env_python = _conda_bin("python")
        run.append_line(f"[runner] interpreter: {env_python}")

        # Layout visualtasksexec: ws-server, frontend, backend em subdirs.
        # Detect e ajusta cwd para o subdir do ws-server (cwd legacy = raiz).
        ws_dir = run.work_dir / "ws-server"
        if ws_dir.exists() and (ws_dir / "main.py").exists():
            run.append_line("[runner] layout visualtasksexec detectado — cwd = ws-server/")
            run.work_dir = ws_dir

        # 2) Checa deps faltantes (sem instalar nada ainda)
        req_file = run.work_dir / "requirements.txt"
        if req_file.exists():
            run.status = "installing"
            run.broadcast_status()
            missing = _check_missing_deps(req_file, run)
            if missing:
                run.append_line(f"[runner] {len(missing)} dep(s) faltando: {', '.join(missing[:10])}{'...' if len(missing) > 10 else ''}")
                ok = _install_missing(req_file, run)
                if not ok:
                    run.status = "crashed"
                    run.exit_code = 1
                    run.finished_at = datetime.utcnow().isoformat()
                    run.broadcast_status()
                    return
            else:
                run.append_line("[runner] todas as deps já estão no env langnet ✓")

        # 3) Sobe python main.py
        main_py = run.work_dir / "main.py"
        if not main_py.exists():
            run.status = "crashed"
            run.append_line("[runner] main.py não encontrado")
            run.broadcast_status()
            return

        run.append_line(f"[ws] starting: {env_python} main.py")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["CREWAI_TESTING"] = env.get("CREWAI_TESTING", "true")
        env["OTEL_SDK_DISABLED"] = env.get("OTEL_SDK_DISABLED", "true")
        # Carrega .env do ws-server (DEEPSEEK_API_KEY etc.) se existir
        _load_env_file_into(env, run.work_dir / ".env")
        _load_env_file_into(env, run.work_dir / ".env.example")  # fallback: usa exemplo
        # Também pega .env do BACKEND principal (LangNet) — DEEPSEEK_API_KEY normalmente vive aí
        _load_env_file_into(env, Path("/home/pasteurjr/progreact/langnet-interface/backend/.env"))

        run.process = subprocess.Popen(
            [str(env_python), "main.py"],
            cwd=str(run.work_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=1,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )

        # Detecta layout visualtasksexec: sobe backend FastAPI + frontend React em paralelo
        root_dir = run.work_dir.parent if run.work_dir.name == "ws-server" else run.work_dir
        backend_dir = root_dir / "backend"
        frontend_dir = root_dir / "frontend"

        side_procs: List[subprocess.Popen] = []
        if backend_dir.exists() and (backend_dir / "main.py").exists():
            run.append_line("[runner] iniciando backend FastAPI...")
            threading.Thread(
                target=_run_backend_service,
                args=(run, backend_dir, env, side_procs),
                daemon=True,
            ).start()
        if frontend_dir.exists() and (frontend_dir / "package.json").exists():
            run.append_line("[runner] iniciando frontend React...")
            threading.Thread(
                target=_run_frontend_service,
                args=(run, frontend_dir, env, side_procs),
                daemon=True,
            ).start()

        run.status = "running"
        run.broadcast_status()

        # Pump stdout até o processo morrer
        try:
            for raw in iter(run.process.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace").rstrip("\n")
                run.append_line(f"[ws] {line}")
        finally:
            try:
                run.process.stdout.close()
            except Exception:
                pass

        # ws-server terminou. Mantém frontend/backend rodando (são independentes)
        # — só derruba todos quando alguém pediu stop_run explicitamente.
        rc = run.process.wait()
        run.exit_code = rc
        run.finished_at = datetime.utcnow().isoformat()
        if run.status == "running":
            run.status = "stopped" if rc == 0 else "crashed"
        run.append_line(f"[ws] process exited (code={rc})")
        # Anexa side_procs ao run pra stop_run poder matar tudo depois
        run.side_processes = side_procs  # noqa: SLF001 (atributo dinâmico)
        run.broadcast_status()

    except Exception as exc:  # noqa: BLE001
        run.status = "crashed"
        run.finished_at = datetime.utcnow().isoformat()
        run.append_line(f"[runner] ERROR: {exc}")
        run.broadcast_status()


def start_run(session_id: str, files: List[Dict[str, Any]]) -> CodeRun:
    """Cria um novo CodeRun e dispara o worker em thread."""
    run_id = str(uuid.uuid4())
    work_dir = RUNS_ROOT / session_id / run_id
    run = CodeRun(
        id=run_id,
        session_id=session_id,
        work_dir=work_dir,
        started_at=datetime.utcnow().isoformat(),
    )
    try:
        run._main_loop = asyncio.get_event_loop()
    except RuntimeError:
        run._main_loop = None
    with _RUNS_LOCK:
        _RUNS[run_id] = run

    th = threading.Thread(target=_worker, args=(run, files), daemon=True)
    th.start()
    return run


def stop_run(run_id: str) -> Optional[CodeRun]:
    run = _RUNS.get(run_id)
    if not run:
        return None
    if run.process and run.process.poll() is None:
        try:
            if os.name == "nt":
                run.process.terminate()
            else:
                os.killpg(os.getpgid(run.process.pid), signal.SIGTERM)
        except Exception:
            try:
                run.process.terminate()
            except Exception:
                pass
        # Aguarda 5s antes de SIGKILL
        try:
            run.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                if os.name == "nt":
                    run.process.kill()
                else:
                    os.killpg(os.getpgid(run.process.pid), signal.SIGKILL)
            except Exception:
                pass
    # Também derruba os side processes (backend FastAPI + frontend React)
    side_procs = getattr(run, "side_processes", []) or []
    for p in side_procs:
        try:
            if p and p.poll() is None:
                if os.name == "nt":
                    p.terminate()
                else:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except Exception:
            pass
    run.status = "stopped"
    run.finished_at = datetime.utcnow().isoformat()
    run.append_line("[runner] stopped by user (ws + backend + frontend)")
    run.broadcast_status()
    return run


def cleanup_old_run_dirs(max_age_hours: int = 24, keep_running: bool = True) -> Dict[str, Any]:
    """Remove diretórios de runs em ``/tmp/langnet-runs/`` mais antigos que
    ``max_age_hours``, preservando os que correspondem a runs ativos no
    registry em memória (se ``keep_running``).

    Retorna ``{removed: [paths], kept: int, freed_bytes: int}``.
    """
    if not RUNS_ROOT.exists():
        return {"removed": [], "kept": 0, "freed_bytes": 0}

    threshold = time.time() - max_age_hours * 3600
    active_run_ids: set = set()
    if keep_running:
        with _RUNS_LOCK:
            for run_id, run in _RUNS.items():
                if run.status in ("preparing", "installing", "running"):
                    active_run_ids.add(run_id)

    removed: List[str] = []
    kept = 0
    freed = 0

    # Estrutura: /tmp/langnet-runs/<session_id>/<run_id>/
    for session_dir in RUNS_ROOT.iterdir():
        if not session_dir.is_dir():
            continue
        for run_dir in session_dir.iterdir():
            if not run_dir.is_dir():
                continue
            if run_dir.name in active_run_ids:
                kept += 1
                continue
            try:
                mtime = run_dir.stat().st_mtime
            except OSError:
                continue
            if mtime > threshold:
                kept += 1
                continue
            # Tamanho antes de remover (best-effort)
            try:
                size = sum(p.stat().st_size for p in run_dir.rglob("*") if p.is_file())
            except OSError:
                size = 0
            try:
                shutil.rmtree(run_dir, ignore_errors=True)
                removed.append(str(run_dir))
                freed += size
            except Exception:
                pass

        # Remove session_dir se vazia depois do cleanup
        try:
            if not any(session_dir.iterdir()):
                session_dir.rmdir()
        except OSError:
            pass

    return {"removed": removed, "kept": kept, "freed_bytes": freed}


def cleanup_run(run_id: str, remove_files: bool = False) -> None:
    """Remove o run do registry e (opcional) apaga work_dir."""
    run = _RUNS.pop(run_id, None)
    if run and remove_files and run.work_dir.exists():
        try:
            shutil.rmtree(run.work_dir, ignore_errors=True)
        except Exception:
            pass


def subscribe(run: CodeRun) -> asyncio.Queue:
    """Adiciona uma fila de subscriber (consumida pelo WS handler)."""
    q: asyncio.Queue = asyncio.Queue(maxsize=2000)
    with run._lock:
        run._subscribers.append(q)
    return q


def unsubscribe(run: CodeRun, q: asyncio.Queue) -> None:
    with run._lock:
        try:
            run._subscribers.remove(q)
        except ValueError:
            pass
