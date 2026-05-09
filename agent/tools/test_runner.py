import subprocess
import sys
import json
import os


class TestRunner:
    """Run pytest on generated test files and return structured results."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def run(self, test_path: str = "tests") -> dict:
        """Run pytest and return parsed results."""
        base = os.path.abspath(self.base_dir)
        test_full_path = os.path.join(base, test_path)
        report_file = ".test_report.json"
        report_path = os.path.join(base, report_file)

        # Add src/ to PYTHONPATH so tests can import generated code
        env = os.environ.copy()
        src_path = os.path.join(base, "src")
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{existing_path}" if existing_path else src_path

        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    test_path,
                    "-v",
                    "--json-report",
                    f"--json-report-file={report_file}",
                ],
                cwd=base,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )

            summary = {
                "exit_code": result.returncode,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "failures": [],
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            # Parse JSON report if available
            if os.path.exists(report_path):
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        report = json.load(f)
                    summary["passed"] = report.get("summary", {}).get("passed", 0)
                    summary["failed"] = report.get("summary", {}).get("failed", 0)
                    summary["errors"] = report.get("summary", {}).get("errors", 0)

                    for test in report.get("tests", []):
                        if test.get("outcome") == "failed":
                            summary["failures"].append({
                                "name": test.get("nodeid", "unknown"),
                                "message": test.get("call", {}).get("longrepr", ""),
                            })
                except (json.JSONDecodeError, KeyError):
                    pass

            # Fallback: parse from text output
            if not summary["failures"] and result.returncode != 0:
                summary["failures"].append({
                    "name": "pytest_output",
                    "message": result.stdout + "\n" + result.stderr,
                })

            return summary

        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "passed": 0, "failed": 0, "errors": 1,
                    "failures": [{"name": "timeout", "message": "Test execution timed out (60s)"}]}

    def passed(self, results: dict) -> bool:
        return results.get("exit_code") == 0 and results.get("failed", 0) == 0
