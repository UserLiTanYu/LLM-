"""测试运行模块 — 封装 pytest 执行和结果解析。

TestRunner 负责：
  1. 在子进程中运行 pytest（60s 超时）
  2. 自动将 src/ 加入 PYTHONPATH（确保测试能导入生成的代码）
  3. 解析 pytest-json-report 的输出获取结构化结果
  4. 回退到文本解析（JSON 报告不可用时）

结果格式：
  {
    "exit_code": int,     # pytest 退出码（0=全部通过）
    "passed": int,        # 通过的测试数
    "failed": int,        # 失败的测试数
    "errors": int,        # 异常数
    "failures": [         # 失败详情列表
      {"name": "测试路径", "message": "错误信息"}
    ],
    "stdout": str,
    "stderr": str,
  }
"""

import subprocess
import sys
import json
import os


class TestRunner:
    """运行 pytest 并返回结构化测试结果。"""

    def __init__(self, base_dir: str):
        """初始化测试运行器。

        参数:
          base_dir: 项目输出根目录（包含 src/ 和 tests/ 子目录）
        """
        self.base_dir = base_dir

    def run(self, test_path: str = "tests") -> dict:
        """执行 pytest 并返回解析后的结果。

        参数:
          test_path: 测试文件目录（相对于 base_dir，默认 "tests"）

        返回:
          结构化的测试结果字典

        执行流程：
          1. 将 src/ 加入 PYTHONPATH
          2. 运行 pytest -v --json-report
          3. 解析 JSON 报告提取通过/失败详情
          4. JSON 不可用时回退到文本解析
        """
        base = os.path.abspath(self.base_dir)
        test_full_path = os.path.join(base, test_path)
        report_file = ".test_report.json"
        report_path = os.path.join(base, report_file)

        # 将 src/ 加入 PYTHONPATH，确保测试能 import 生成的模块
        env = os.environ.copy()
        src_path = os.path.join(base, "src")
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{existing_path}" if existing_path else src_path

        try:
            # 运行 pytest，启用 JSON 报告插件
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    test_path,
                    "-v",                                     # 详细输出
                    "--json-report",                          # 启用 JSON 报告
                    f"--json-report-file={report_file}",      # 指定报告文件路径
                ],
                cwd=base,
                capture_output=True,
                text=True,
                timeout=60,                                   # 60 秒超时保护
                env=env,
            )

            # 构建结果摘要
            summary = {
                "exit_code": result.returncode,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "failures": [],
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            # 解析 pytest-json-report 生成的 JSON 文件
            if os.path.exists(report_path):
                try:
                    with open(report_path, "r", encoding="utf-8") as f:
                        report = json.load(f)
                    summary["passed"] = report.get("summary", {}).get("passed", 0)
                    summary["failed"] = report.get("summary", {}).get("failed", 0)
                    summary["errors"] = report.get("summary", {}).get("errors", 0)

                    # 提取每个失败测试的详细信息
                    for test in report.get("tests", []):
                        if test.get("outcome") == "failed":
                            summary["failures"].append({
                                "name": test.get("nodeid", "unknown"),
                                "message": test.get("call", {}).get("longrepr", ""),
                            })
                except (json.JSONDecodeError, KeyError):
                    pass  # JSON 解析失败时忽略，使用默认值

            # 回退：JSON 报告不存在或无失败详情时，用原始文本输出填充
            if not summary["failures"] and result.returncode != 0:
                summary["failures"].append({
                    "name": "pytest_output",
                    "message": result.stdout + "\n" + result.stderr,
                })

            return summary

        except subprocess.TimeoutExpired:
            # 测试执行超时
            return {"exit_code": -1, "passed": 0, "failed": 0, "errors": 1,
                    "failures": [{"name": "timeout", "message": "测试执行超时 (60s)"}]}

    def passed(self, results: dict) -> bool:
        """判断测试是否全部通过。

        参数:
          results: run() 返回的结果字典

        返回:
          全部通过返回 True，否则返回 False
        """
        return results.get("exit_code") == 0 and results.get("failed", 0) == 0
