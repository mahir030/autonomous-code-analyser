import subprocess
import tempfile
import os
import shutil
import time
from analyzers.resource_limiter import set_limits


class SandboxExecutor:

    def __init__(self, timeout=3):
        self.timeout = timeout

    def _preexec(self):
        set_limits()

    def execute(self, command, cwd=None):
        start_time = time.time()

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                preexec_fn=self._preexec
            )

            stdout, stderr = process.communicate(timeout=self.timeout)

            runtime = time.time() - start_time

            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "runtime": round(runtime, 4),
                "stdout": stdout.decode(errors="ignore")[:500],
                "stderr": stderr.decode(errors="ignore")[:500]
            }

        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "success": False,
                "exit_code": -1,
                "runtime": self.timeout,
                "stdout": "",
                "stderr": "Execution timed out"
            }

        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "runtime": 0,
                "stdout": "",
                "stderr": str(e)
            }

