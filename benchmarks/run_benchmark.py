"""Run all benchmark cases and produce a summary report."""
import sys
import os
import time
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config import AgentConfig
from agent.orchestrator import SEAgent

BENCHMARKS_DIR = os.path.dirname(os.path.abspath(__file__))
CASES_DIR = os.path.join(BENCHMARKS_DIR, "cases")

CASES = [
    ("case1_calculator", "计算器模块"),
    ("case2_user_mgmt", "用户管理系统"),
    ("case3_order_state", "订单状态机"),
    ("case4_scheduler", "任务调度器"),
    ("case5_todo_api", "TODO API服务"),
]


def run_benchmark():
    config = AgentConfig.from_env()
    if not config.api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量")
        sys.exit(1)

    results = []

    for case_id, case_name in CASES:
        case_dir = os.path.join(CASES_DIR, case_id)
        req_file = os.path.join(case_dir, "requirements.md")
        output_dir = os.path.join(BENCHMARKS_DIR, "results", case_id)

        if not os.path.exists(req_file):
            print(f"\n[跳过] {case_name}: 需求文件不存在")
            continue

        print(f"\n{'=' * 60}")
        print(f"  测试用例: {case_name} ({case_id})")
        print(f"{'=' * 60}")

        config.output_dir = output_dir
        start_time = time.time()

        try:
            agent = SEAgent(config)
            requirements = open(req_file, "r", encoding="utf-8").read()
            state = agent.run(requirements)

            tr = state.get("test_results", {})
            tests_passed = tr.get("passed", 0)
            tests_failed = tr.get("failed", 0)
            total = tests_passed + tests_failed
            pass_rate = (tests_passed / total * 100) if total > 0 else 0

            results.append({
                "case": case_name,
                "case_id": case_id,
                "passed": tests_passed,
                "failed": tests_failed,
                "total": total,
                "pass_rate": round(pass_rate, 1),
                "iterations": state.get("iteration", 0),
                "test_passed": state.get("test_passed", False),
                "tokens": agent.llm.token_usage,
                "time": round(time.time() - start_time, 1),
            })

        except Exception as e:
            results.append({
                "case": case_name,
                "case_id": case_id,
                "passed": 0,
                "failed": 0,
                "total": 0,
                "pass_rate": 0,
                "iterations": 0,
                "test_passed": False,
                "error": str(e),
                "time": round(time.time() - start_time, 1),
            })

    # Print summary
    print("\n" + "=" * 70)
    print("  基准测试结果汇总")
    print("=" * 70)
    print(f"{'场景':<16} {'用例数':<8} {'通过':<6} {'失败':<6} {'通过率':<8} {'状态':<10}")
    print("-" * 70)

    total_passed = 0
    total_tests = 0
    for r in results:
        status = "通过" if r["test_passed"] else ("错误" if r.get("error") else "未通过")
        print(f"{r['case']:<16} {r['total']:<8} {r['passed']:<6} {r['failed']:<6} "
              f"{r['pass_rate']}%{'':<5} {status:<10}")
        total_passed += r["passed"]
        total_tests += r["total"]

    print("-" * 70)
    overall = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"  总计: {total_passed}/{total_tests} ({overall:.1f}%)")

    # Save report
    report_path = os.path.join(BENCHMARKS_DIR, "results", "summary.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n详细报告: {report_path}")
    return results


if __name__ == "__main__":
    run_benchmark()
