from agent.llm.gateway import LLMGateway
from agent.llm.prompts import REPAIR_SYSTEM
from agent.tools.file_manager import FileManager, parse_code_files


def run_repair_node(llm: LLMGateway, code_output: str, test_output: str,
                    failures: list[dict], fm: FileManager) -> dict:
    """Analyze test failures and repair code. Returns state update dict."""
    print(f"[Repair] 分析 {len(failures)} 个测试失败，尝试修复...")

    failure_text = "\n\n".join(
        f"失败测试: {f['name']}\n错误信息: {f['message']}" for f in failures
    )

    prompt = f"""## 当前代码
{code_output}

## 测试代码
{test_output}

## 测试失败信息
{failure_text}

请定位Bug根因并修复代码。"""

    messages = [
        {"role": "system", "content": REPAIR_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    repair_output = llm.chat(messages)

    # Parse repaired code files
    files = parse_code_files(repair_output)
    repaired = False
    for filename, content in files.items():
        path = f"src/{filename}" if not filename.startswith("src/") else filename
        fm.write(path, content)
        repaired = True

    if not repaired:
        # Try to extract code from the repair output (might be wrapped differently)
        fm.write("src/repair_analysis.md", repair_output)

    print(f"[Repair] 修复完成，已更新 {len(files)} 个文件")
    return {"repair_output": repair_output, "code_output": repair_output, "code_files": files}
