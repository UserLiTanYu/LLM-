"""测试节点 — 调用 LLM 生成测试用例并执行 pytest。

流程：
  1. 将需求文档 + 实现代码发送给 LLM，生成 pytest 测试
  2. 正则解析测试文件，写入 tests/ 目录
  3. 调用 TestRunner 执行 pytest（30s 超时）
  4. 收集并返回测试结果

TestRunner 会自动将 src/ 加入 PYTHONPATH，
确保测试代码能正确导入生成的模块。
"""

from agent.llm.gateway import LLMGateway
from agent.llm.prompts import TEST_SYSTEM
from agent.tools.file_manager import FileManager, parse_code_files
from agent.tools.test_runner import TestRunner


def run_test_node(llm: LLMGateway, requirements: str, code_output: str,
                  fm: FileManager, test_runner: TestRunner) -> dict:
    """生成测试用例并执行。返回状态更新字典。

    参数:
      llm:          LLM 网关实例
      requirements: 需求文档原始文本
      code_output:  已生成的实现代码（原始 LLM 输出）
      fm:           文件管理器
      test_runner:  pytest 运行器

    返回:
      {"test_output": 原始LLM输出, "test_results": 测试结果摘要, "test_passed": 是否全部通过}
    """
    print("[Test] 生成测试用例并执行...")

    # 拼接需求 + 实现代码作为 LLM 输入
    prompt = f"""## 需求文档
{requirements}

## 实现代码
{code_output}

请生成完整的pytest测试用例。"""

    messages = [
        {"role": "system", "content": TEST_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    # 调用 LLM 生成测试代码
    test_output = llm.chat(messages)

    # 解析并保存测试文件
    files = parse_code_files(test_output)
    for filename, content in files.items():
        path = f"tests/{filename}" if not filename.startswith("tests/") else filename
        fm.write(path, content)

    if not files:
        # 回退：无法解析时保存原始输出
        fm.write("tests/test_generated.py", test_output)

    # 执行 pytest 并收集结果
    results = test_runner.run("tests")
    passed = test_runner.passed(results)

    print(f"[Test] 测试结果: {'全部通过' if passed else '存在失败'} "
          f"(通过{results['passed']}, 失败{results['failed']})")

    return {
        "test_output": test_output,
        "test_results": results,
        "test_passed": passed,
    }
