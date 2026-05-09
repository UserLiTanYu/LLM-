import subprocess
import sys
from agent.tools.file_manager import FileManager


class CodeExecutor:
    """Execute generated Python code in a subprocess."""

    def __init__(self, file_manager: FileManager):
        self.fm = file_manager

    def run(self, script_relative_path: str, args: list[str] | None = None) -> dict:
        """Run a Python script and return {exit_code, stdout, stderr}."""
        script_path = script_relative_path
        try:
            result = subprocess.run(
                [sys.executable, script_path] + (args or []),
                cwd=self.fm.base_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "stdout": "", "stderr": "Execution timed out (30s)"}

    def check_syntax(self, script_relative_path: str) -> dict:
        """Check Python syntax of a file. Returns {ok, message}."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", script_relative_path],
                cwd=self.fm.base_dir,
                capture_output=True,
                text=True,
            )
            return {"ok": result.returncode == 0, "message": result.stderr or "Syntax OK"}
        except Exception as e:
            return {"ok": False, "message": str(e)}
