"""Loopback-only, authenticated runner for trusted personal practice code.

This is a local development tool, not a sandbox for untrusted submissions.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.metadata
import json
import os
from pathlib import Path
import re
import signal
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import parse_qs, urlparse

from exercises import load_exercise

TOKEN = os.environ.get("PRACTICE_RUNNER_TOKEN", "")
JOBS = {}
LOCK = threading.Lock()
SLOTS = threading.BoundedSemaphore(2)
PACKAGES = {"torch": "torch", "numpy": "numpy", "scipy": "scipy", "pandas": "pandas",
            "sklearn": "scikit-learn", "matplotlib": "matplotlib", "PIL": "pillow",
            "sympy": "sympy", "sortedcontainers": "sortedcontainers", "pytest": "pytest", "jax": "jax"}


def stop(process):
    if process and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def cancel(job_id):
    with LOCK:
        job = JOBS.get(job_id)
        if job:
            job["cancelled"] = True
            stop(job.get("process"))
            return True
    return False


def execute(request):
    job_id = request.get("id", "")
    if not re.fullmatch(r"[a-zA-Z0-9-]{8,80}", job_id):
        raise ValueError("Invalid run id")
    if not isinstance(request.get("code"), str) or not all(isinstance(request.get(k, ""), str) for k in ("tests", "stdin")):
        raise ValueError("Code, tests and stdin must be strings")
    if sum(len(request.get(k, "")) for k in ("code", "tests", "stdin")) > 200_000:
        raise ValueError("Code is too large")
    timeout = min(30, max(1, float(request.get("timeout", 15))))
    if not SLOTS.acquire(blocking=False):
        raise ValueError("Runner busy: wait for an existing run to finish")
    with LOCK:
        if job_id in JOBS:
            SLOTS.release()
            raise ValueError("Duplicate run id")
        JOBS[job_id] = {"cancelled": False, "process": None}
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="handbook-run-") as directory:
            directory = Path(directory)
            input_file, result_file = directory / "request.json", directory / "result.json"
            input_file.write_text(json.dumps(request))
            environment = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "LANG") if key in os.environ}
            environment.update({"HOME": str(directory), "TMPDIR": str(directory), "MPLBACKEND": "Agg",
                                "MPLCONFIGDIR": str(Path(sys.prefix) / "practice-matplotlib"), "OMP_NUM_THREADS": "1",
                                "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "PYTHONHASHSEED": "0", "JAX_PLATFORMS": "cpu"})
            language = request.get("language", "python")
            if language == "javascript":
                binary = shutil.which("node")
                if not binary:
                    raise ValueError("Node.js is not installed")
                (directory / "node_modules").symlink_to(Path(__file__).resolve().parents[2] / "node_modules", target_is_directory=True)
                command = [binary, str(Path(__file__).with_name("execute-js.mjs")), str(input_file), str(result_file)]
            elif language == "python":
                command = [sys.executable, "-I", "-u", str(Path(__file__).with_name("execute.py")), str(input_file), str(result_file)]
            else:
                raise ValueError("Unsupported language")
            with (directory / "stdout").open("wb") as stdout, (directory / "stderr").open("wb") as stderr:
                process = subprocess.Popen(command, cwd=directory, env=environment,
                                           stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
                with LOCK:
                    JOBS[job_id]["process"] = process
                reason = None
                while True:
                    with LOCK:
                        cancelled = JOBS[job_id]["cancelled"]
                    if cancelled:
                        reason = "cancelled"
                    elif time.monotonic() - started > timeout:
                        reason = "timeout"
                    elif sum((directory / name).stat().st_size for name in ("stdout", "stderr")) > 200_000:
                        reason = "output_limit"
                    if reason:
                        stop(process)
                        break
                    if process.poll() is not None:
                        break
                    time.sleep(0.03)
                process.wait()
                # Also reap descendants when the main script has already exited.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            result = json.loads(result_file.read_text()) if result_file.exists() and not reason else {
                "status": reason or "failed", "checks": [], "plots": [], "error": None,
            }
            result.update({"id": job_id, "durationMs": round((time.monotonic() - started) * 1000),
                           "stdout": (directory / "stdout").read_bytes()[:100_000].decode(errors="replace"),
                           "stderr": (directory / "stderr").read_bytes()[:100_000].decode(errors="replace"),
                           "exitCode": process.returncode})
            return result
    finally:
        with LOCK:
            JOBS.pop(job_id, None)
        SLOTS.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def authorized(self):
        if not TOKEN or self.headers.get("Authorization") != "Bearer " + TOKEN:
            self.reply(403, {"error": "Local runner authentication required"})
            return False
        return True

    def do_GET(self):
        if not self.authorized():
            return
        url = urlparse(self.path)
        if url.path == "/health":
            packages = {}
            for module, distribution in PACKAGES.items():
                try:
                    packages[module] = importlib.metadata.version(distribution)
                except importlib.metadata.PackageNotFoundError:
                    packages[module] = None
            self.reply(200, {"python": sys.version.split()[0], "packages": packages, "device": "cpu"})
        elif url.path == "/exercise":
            query = parse_qs(url.query)
            try:
                self.reply(200, load_exercise(query.get("book", [""])[0], query.get("question", [""])[0]))
            except (ValueError, SyntaxError, OSError) as error:
                self.reply(400, {"error": str(error)})
        else:
            self.reply(404, {"error": "Not found"})

    def do_POST(self):
        if not self.authorized():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 1_000_000:
                raise ValueError("Invalid request size")
            request = json.loads(self.rfile.read(length))
            if not isinstance(request, dict):
                raise ValueError("Expected JSON object")
            if self.path == "/run":
                self.reply(200, execute(request))
            elif self.path == "/stop":
                self.reply(200, {"stopped": cancel(str(request.get("id", "")))})
            else:
                self.reply(404, {"error": "Not found"})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.reply(400, {"error": str(error)})


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Start with npm run practice (runner token is required).")
    server = ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PRACTICE_RUNNER_PORT", "8765"))), Handler)
    server.daemon_threads = True
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    print("Local Python runner ready", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        with LOCK:
            for job in JOBS.values():
                stop(job.get("process"))
