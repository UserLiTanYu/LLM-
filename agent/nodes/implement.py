from agent.llm.gateway import LLMGateway
from agent.llm.prompts import IMPLEMENT_SYSTEM
from agent.tools.file_manager import FileManager, parse_code_files


def run_implement_node(llm: LLMGateway, requirements: str, design: str, fm: FileManager) -> dict:
    """Generate Python code from requirements and design. Returns state update dict."""
    print("[Implement] 根据需求和设计生成代码...")

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

    code_output = llm.chat(messages)

    # Parse code files from LLM output
    files = parse_code_files(code_output)
    if not files:
        # If parsing failed, save raw output
        fm.write("src/generated_code.py", code_output)
        files = {"generated_code.py": code_output}

    for filename, content in files.items():
        path = f"src/{filename}" if not filename.startswith("src/") else filename
        fm.write(path, content)

    print(f"[Implement] 已生成 {len(files)} 个文件 → src/")
    return {"code_files": files, "code_output": code_output}
