"""修复节点 — 分析测试失败并自动修复代码。

流程：
  1. 收集测试失败信息（测试名称 + 错误消息）
  2. 将代码 + 测试代码 + 失败信息发送给 LLM（使用 REPAIR_SYSTEM 角色）
  3. LLM 返回修复方案和修复后代码
  4. 解析修复后的代码，覆盖 src/ 中的对应文件
  5. 编排器会重新进入测试节点验证修复结果

这个修复循环最多迭代 max_repair_iterations 次（默认 3 次），
如果修复后测试仍失败且未超限，会再次触发此节点。
"""

from agent.llm.gateway import LLMGateway
from agent.llm.prompts import REPAIR_SYSTEM
from agent.tools.file_manager import FileManager, parse_code_files


def run_repair_node(llm: LLMGateway, code_output: str, test_output: str,
                    failures: list[dict], fm: FileManager) -> dict:
    """分析测试失败并修复代码。返回状态更新字典。

    参数:
      llm:         LLM 网关实例
      code_output: 当前代码（原始 LLM 输出）
      test_output: 测试代码（原始 LLM 输出）
      failures:    失败列表 [{"name": 测试名, "message": 错误信息}, ...]
      fm:          文件管理器

    返回:
      {"repair_output": 修复方案全文, "code_output": 修复后代码, "code_files": {文件名: 内容}}
    """
    print(f"[Repair] 分析 {len(failures)} 个测试失败，尝试修复...")

    # 格式化测试失败信息
    failure_text = "\n\n".join(
        f"失败测试: {f['name']}\n错误信息: {f['message']}" for f in failures
    )

    # 拼接修复上下文：代码 + 测试 + 失败信息
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

    # 调用 LLM 生成修复方案
    repair_output = llm.chat(messages)

    # 解析修复后的代码文件，覆盖写入 src/
    files = parse_code_files(repair_output)
    repaired = False
    for filename, content in files.items():
        path = f"src/{filename}" if not filename.startswith("src/") else filename
        fm.write(path, content)
        repaired = True

    if not repaired:
        # 回退：无法解析出代码时，保存修复分析文档
        fm.write("src/repair_analysis.md", repair_output)

    print(f"[Repair] 修复完成，已更新 {len(files)} 个文件")
    return {"repair_output": repair_output, "code_output": repair_output, "code_files": files}
