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

        run.append_line(f"[runner] starting: {env_python} main.py")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        # Carrega .env do projeto se existir
        run.process = subprocess.Popen(
            [str(env_python), "main.py"],
            cwd=str(run.work_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            bufsize=1,
            preexec_fn=os.setsid if os.name != "nt" else None,
        )
        run.status = "running"
        run.broadcast_status()

        # Pump stdout até o processo morrer
        try:
            for raw in iter(run.process.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace").rstrip("\n")
                run.append_line(line)
        finally:
            try:
                run.process.stdout.close()
            except Exception:
                pass

        # Process terminou
        rc = run.process.wait()
        run.exit_code = rc
        run.finished_at = datetime.utcnow().isoformat()
        if run.status == "running":
            run.status = "stopped" if rc == 0 else "crashed"
        run.append_line(f"[runner] process exited (code={rc})")
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
    run.status = "stopped"
    run.finished_at = datetime.utcnow().isoformat()
    run.append_line("[runner] stopped by user")
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
