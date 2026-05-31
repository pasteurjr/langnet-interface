"""
Subprocess runner para o sistema agêntico gerado.

Pipeline ao iniciar um run:
1. Cria /tmp/langnet-runs/<session_id>/<run_id>/
2. Escreve arquivos da sessão lá dentro
3. Cria venv local
4. pip install -r requirements.txt (com timeout)
5. Sobe `python main.py` em background
6. Stream stdout/stderr para buffer em memória + asyncio.Queue (consumido pelo WS)

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
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


RUNS_ROOT = Path(os.environ.get("LANGNET_RUNS_ROOT", "/tmp/langnet-runs"))
PIP_TIMEOUT_SECONDS = 600  # 10 min para instalar deps
MAX_STDOUT_LINES = 5000     # buffer cap (linhas anteriores ficam — só limita memória)


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


def _worker(run: CodeRun, files: List[Dict[str, Any]]) -> None:
    """Thread worker: cria venv, instala deps, sobe main.py, faz tail."""
    try:
        # 1) Escreve arquivos
        run.append_line(f"[runner] writing {len(files)} file(s) to {run.work_dir}")
        _safe_write_files(run.work_dir, files)

        # 2) Cria venv
        venv_dir = run.work_dir / ".venv"
        if not venv_dir.exists():
            run.status = "installing"
            run.broadcast_status()
            run.append_line(f"[runner] creating venv at {venv_dir}")
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                cwd=str(run.work_dir),
                check=True,
                capture_output=True,
            )

        venv_python = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
        venv_pip = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("pip.exe" if os.name == "nt" else "pip")

        # 3) pip install -r requirements.txt
        req_file = run.work_dir / "requirements.txt"
        if req_file.exists():
            run.append_line(f"[runner] pip install -r requirements.txt (timeout {PIP_TIMEOUT_SECONDS}s)")
            try:
                proc = subprocess.Popen(
                    [str(venv_pip), "install", "--no-cache-dir", "-r", "requirements.txt"],
                    cwd=str(run.work_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,
                )
                # Lê output linha-a-linha
                for raw in iter(proc.stdout.readline, b""):
                    line = raw.decode("utf-8", errors="replace").rstrip("\n")
                    run.append_line(f"[pip] {line}")
                proc.wait(timeout=PIP_TIMEOUT_SECONDS)
                if proc.returncode != 0:
                    run.status = "crashed"
                    run.exit_code = proc.returncode
                    run.finished_at = datetime.utcnow().isoformat()
                    run.append_line(f"[runner] pip install FAILED (exit {proc.returncode})")
                    run.broadcast_status()
                    return
            except subprocess.TimeoutExpired:
                run.status = "crashed"
                run.append_line("[runner] pip install TIMEOUT")
                run.broadcast_status()
                return

        # 4) Sobe python main.py
        main_py = run.work_dir / "main.py"
        if not main_py.exists():
            run.status = "crashed"
            run.append_line("[runner] main.py não encontrado")
            run.broadcast_status()
            return

        run.append_line(f"[runner] starting: {venv_python} main.py")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        # Carrega .env do projeto se existir
        run.process = subprocess.Popen(
            [str(venv_python), "main.py"],
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
