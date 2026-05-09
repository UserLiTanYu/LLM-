import os
import re


class FileManager:
    """Read and write files in the output directory."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def write(self, relative_path: str, content: str):
        """Write content to a file under base_dir."""
        full_path = os.path.join(self.base_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read(self, relative_path: str) -> str:
        """Read a file from base_dir."""
        full_path = os.path.join(self.base_dir, relative_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def list_dir(self, relative_path: str = ".") -> list[str]:
        """List files under a directory."""
        full_path = os.path.join(self.base_dir, relative_path)
        if not os.path.exists(full_path):
            return []
        result = []
        for root, dirs, files in os.walk(full_path):
            for f in files:
                result.append(os.path.relpath(os.path.join(root, f), self.base_dir))
        return result


def parse_code_files(llm_output: str) -> dict[str, str]:
    """Parse LLM output containing ```python:filename.py blocks into {filename: content} dict."""
    pattern = r"```python:([^\n]+)\n(.*?)```"
    matches = re.findall(pattern, llm_output, re.DOTALL)
    if not matches:
        # Fallback: try ```python blocks without filenames
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, llm_output, re.DOTALL)
        if matches:
            return {f"generated_{i}.py": code.strip() for i, code in enumerate(matches)}
    return {filename.strip(): code.strip() for filename, code in matches}
