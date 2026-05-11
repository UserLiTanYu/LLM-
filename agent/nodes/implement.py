"""实现节点 — 调用 LLM 将设计方案转化为可运行的 Python 代码。

输入：需求文档 + 设计方案
输出：多个 Python 源文件，写入 src/ 目录

代码生成流程：
  1. 拼接需求 + 设计方案作为 User Prompt
  2. 使用 IMPLEMENT_SYSTEM 角色调用 LLM
  3. 通过 parse_code_files() 正则提取 ```python:filename.py``` 块
  4. 将每个提取出的文件写入 src/ 子目录

如果 LLM 输出格式不符合预期（无法提取代码块），
则回退为将原始输出作为 generated_code.py 保存。
"""

from agent.llm.gateway import LLMGateway
from agent.llm.prompts import IMPLEMENT_SYSTEM
from agent.tools.file_manager import FileManager, parse_code_files


def run_implement_node(llm: LLMGateway, requirements: str, design: str, fm: FileManager) -> dict:
    """根据需求和设计生成 Python 代码。返回状态更新字典。

    参数:
      llm:          LLM 网关实例
      requirements: 需求文档原始文本
      design:       设计方案全文（来自设计节点）
      fm:           文件管理器

    返回:
      {"code_output": 原始 LLM 输出, "code_files": {文件名: 代码内容}}
    """
    print("[Implement] 根据需求和设计生成代码...")

    # 拼接需求 + 方案作为 User Prompt
    prompt = f"""## 需求文档
{requirements}

## 设计方案
{design}

请根据以上需求和设计，生成完整的Python代码。
请先列出文件结构，再逐个输出文件内容。"""

    messages = [
        {"role": "system", "content": IMPLEMENT_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    # 调用 LLM 生成代码
    code_output = llm.chat(messages)

    # 用正则从 LLM 输出中解析代码文件
    files = parse_code_files(code_output)
    if not files:
        # 回退：无法解析时，将原始输出整体保存
        fm.write("src/generated_code.py", code_output)
        files = {"generated_code.py": code_output}

    # 将每个解析出的文件写入 src/ 目录
    for filename, content in files.items():
        path = f"src/{filename}" if not filename.startswith("src/") else filename
        fm.write(path, content)

    print(f"[Implement] 已生成 {len(files)} 个文件 → src/")
    return {"code_files": files, "code_output": code_output}
