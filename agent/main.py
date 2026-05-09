"""CLI entry point for the Software Engineering Agent.

Usage:
    python -m agent.main --task generate --input requirements.md --output output/
    python -m agent.main --task design --input requirements.md --output output/
    python -m agent.main --task generate --input requirements.md --output output/ --api-key sk-xxx
"""

import argparse
import os
import sys

from agent.config import AgentConfig
from agent.orchestrator import SEAgent


def main():
    parser = argparse.ArgumentParser(
        description="LLM-based Software Engineering Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agent.main --task generate --input req.md --output out/
  python -m agent.main --task design --input req.md --output out/
  python -m agent.main --task generate --input req.md --output out/ --api-key sk-xxx
        """,
    )
    parser.add_argument("--task", choices=["generate", "design"], default="generate",
                        help="Task to run: generate (full pipeline) or design (design only)")
    parser.add_argument("--input", required=True, help="Path to requirements markdown file")
    parser.add_argument("--output", default="output", help="Output directory (default: output)")
    parser.add_argument("--api-key", default="", help="DeepSeek API key (or set DEEPSEEK_API_KEY env var)")
    parser.add_argument("--base-url", default="", help="API base URL (or set DEEPSEEK_BASE_URL env var)")
    parser.add_argument("--max-repair", type=int, default=3, help="Max repair iterations (default: 3)")

    args = parser.parse_args()

    # Override config from CLI args
    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
    if args.base_url:
        os.environ["DEEPSEEK_BASE_URL"] = args.base_url

    config = AgentConfig()
    config.output_dir = args.output
    config.max_repair_iterations = args.max_repair

    if not config.api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量或通过 --api-key 参数提供")
        sys.exit(1)

    # Read input
    input_path = args.input
    if not os.path.exists(input_path):
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        requirements = f.read()

    print(f"输入文件: {args.input}")
    print(f"输出目录: {args.output}")
    print(f"执行任务: {args.task}")
    print(f"LLM模型: {config.model}")

    if args.task == "design":
        from agent.tools.file_manager import FileManager
        from agent.llm.gateway import LLMGateway
        from agent.nodes.design import run_design_node

        llm = LLMGateway(config)
        fm = FileManager(config.output_dir)
        run_design_node(llm, requirements, fm)
    else:
        agent = SEAgent(config)
        agent.run(requirements)


if __name__ == "__main__":
    main()
