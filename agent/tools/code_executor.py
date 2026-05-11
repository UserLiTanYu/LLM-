"""代码执行模块 — 在子进程中安全执行生成的 Python 代码。

CodeExecutor 用于沙箱化运行生成的代码，避免影响主进程。
通过 subprocess 子进程执行，设置 30 秒超时防止死循环。
"""

import subprocess
import sys
from agent.tools.file_manager import FileManager


class CodeExecutor:
    """在子进程中执行生成的 Python 代码，提供安全隔离。

    使用 subprocess.run 在子进程中运行脚本，
    自动捕获 stdout/stderr，设置超时保护。
    """

    def __init__(self, file_manager: FileManager):
        """初始化代码执行器。

        参数:
          file_manager: 文件管理器（用于定位要执行的脚本）
        """
        self.fm = file_manager

    def run(self, script_relative_path: str, args: list[str] | None = None) -> dict:
        """运行 Python 脚本并返回执行结果。

        参数:
          script_relative_path: 要执行的脚本相对路径
          args:                 可选命令行参数列表

        返回:
          {"exit_code": 退出码, "stdout": 标准输出, "stderr": 标准错误}

        超时（30s）时返回 exit_code=-1。
        """
        script_path = script_relative_path
        try:
            result = subprocess.run(
                [sys.executable, script_path] + (args or []),
                cwd=self.fm.base_dir,      # 在输出目录下执行
                capture_output=True,        # 捕获标准输出/错误
                text=True,
                timeout=30,                 # 30 秒超时保护
            )
            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"exit_code": -1, "stdout": "", "stderr": "执行超时 (30s)"}

    def check_syntax(self, script_relative_path: str) -> dict:
        """检查 Python 文件的语法是否正确。

        使用 py_compile 模块编译文件，
        不实际执行，只检查语法和编译时错误。

        参数:
          script_relative_path: 要检查的脚本相对路径

        返回:
          {"ok": 语法是否合法, "message": 错误信息或 "Syntax OK"}
        """
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
