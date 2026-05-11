"""文件管理模块 — 提供生成文件的基础读写操作。

FileManager:  管理 output/ 目录下的文件读写
parse_code_files(): 从 LLM 输出中提取 Python 代码文件

代码解析规则：
  优先匹配 ```python:filename.py``` 格式（带文件名）
  回退匹配 ```python``` 格式（不带文件名，自动编号）
"""

import os
import re


class FileManager:
    """管理输出目录中的文件读写。

    所有路径均相对于 base_dir（通常为 output/），
    自动创建不存在的父目录。
    """

    def __init__(self, base_dir: str):
        """初始化文件管理器。

        参数:
          base_dir: 输出根目录（如 "output" 或 "./output"）
        """
        self.base_dir = base_dir

    def write(self, relative_path: str, content: str):
        """将内容写入 base_dir 下的相对路径。

        参数:
          relative_path: 相对路径（如 "src/calculator.py"）
          content:       要写入的文本内容

        会自动创建路径中不存在的目录。
        """
        full_path = os.path.join(self.base_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read(self, relative_path: str) -> str:
        """从 base_dir 读取文件。

        参数:
          relative_path: 相对路径

        返回:
          文件内容字符串
        """
        full_path = os.path.join(self.base_dir, relative_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_dir(self, relative_path: str = ".") -> list[str]:
        """递归列出目录下的所有文件。

        参数:
          relative_path: 相对于 base_dir 的目录路径

        返回:
          相对路径列表（相对于 base_dir）
        """
        full_path = os.path.join(self.base_dir, relative_path)
        if not os.path.exists(full_path):
            return []
        result = []
        for root, dirs, files in os.walk(full_path):
            for f in files:
                result.append(os.path.relpath(os.path.join(root, f), self.base_dir))
        return result


def parse_code_files(llm_output: str) -> dict[str, str]:
    """从 LLM 输出中解析代码文件，支持多种语言。

    解析策略（按优先级）：
      1. 匹配 ```语言:文件路径\n...``` 带文件名的代码块（如 python:app.py、html:templates/index.html）
      2. 回退：匹配 ```语言\n...``` 不带文件名的代码块，自动编号

    支持的语言标记：python、html、css、javascript、js

    参数:
      llm_output: LLM 返回的原始文本

    返回:
      {文件路径: 代码内容} 字典
    """
    # 优先：匹配带文件名的代码块 ```lang:path/file.ext
    pattern = r"```(\w+):([^\n]+)\n(.*?)```"
    matches = re.findall(pattern, llm_output, re.DOTALL)
    if matches:
        return {filename.strip(): code.strip() for lang, filename, code in matches}

    # 回退：匹配不带文件名的代码块 ```lang
    pattern = r"```(\w+)\n(.*?)```"
    raw = re.findall(pattern, llm_output, re.DOTALL)
    if raw:
        # 根据语言类型确定扩展名
        ext_map = {"python": "py", "html": "html", "css": "css", "javascript": "js", "js": "js"}
        files = {}
        for i, (lang, code) in enumerate(raw):
            ext = ext_map.get(lang, "txt")
            files[f"generated_{i}.{ext}"] = code.strip()
        return files

    return {}
