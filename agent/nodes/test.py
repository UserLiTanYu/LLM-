from agent.llm.gateway import LLMGateway
from agent.llm.prompts import TEST_SYSTEM
from agent.tools.file_manager import FileManager, parse_code_files
from agent.tools.test_runner import TestRunner


def run_test_node(llm: LLMGateway, requirements: str, code_output: str,
                  fm: FileManager, test_runner: TestRunner) -> dict:
    """Generate and execute tests. Returns state update dict."""
    print("[Test] 生成测试用例并执行...")

    prompt = f"""## 需求文档
{requirements}

## 实现代码
{code_output}

请生成完整的pytest测试用例。"""

    messages = [
        {"role": "system", "content": TEST_SYSTEM},
        {"role": "user", "content": prompt},
    ]

    test_output = llm.chat(messages)

    # Parse and save test files
    files = parse_code_files(test_output)
    for filename, content in files.items():
        path = f"tests/{filename}" if not filename.startswith("tests/") else filename
        fm.write(path, content)

    if not files:
        fm.write("tests/test_generated.py", test_output)

    # Run tests
    results = test_runner.run("tests")
    passed = test_runner.passed(results)

    print(f"[Test] 测试结果: {'全部通过' if passed else '存在失败'} "
          f"(通过{results['passed']}, 失败{results['failed']})")

    return {
        "test_output": test_output,
        "test_results": results,
        "test_passed": passed,
    }
