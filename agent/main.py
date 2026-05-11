"""CLI 入口模块 — 软件工程智能体的命令行入口。

使用方式：
    python -m agent --task design --input requirements.md --output output/
    python -m agent --task implement --input requirements.md --output output/
    python -m agent --task test --input requirements.md --output output/
    python -m agent --task generate --input requirements.md --output output/

支持五种任务模式：
  - design:    仅设计方案
  - implement: 设计 → 实现（生成代码）
  - test:      设计 → 实现 → 测试（不进修复循环）
  - repair:    设计 → 实现 → 测试 → 修复（含循环）
  - generate:  同 repair，完整流水线

参数说明：
  --task       任务类型，默认 generate
  --input      需求文档路径（Markdown 格式）
  --output     输出目录，默认 output/
  --api-key    DeepSeek API 密钥，也可通过环境变量 DEEPSEEK_API_KEY 设置
  --base-url   API 地址，也可通过环境变量 DEEPSEEK_BASE_URL 设置
  --max-repair 最大修复迭代次数，默认 3
"""

import argparse
import os
import sys

from agent.config import AgentConfig
from agent.orchestrator import SEAgent


def main():
    """命令行主函数 — 解析参数、初始化配置、启动智能体流水线。"""

    # 构建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="LLM-based Software Engineering Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agent --task design    --input req.md --output out/
  python -m agent --task implement --input req.md --output out/
  python -m agent --task test      --input req.md --output out/
  python -m agent --task generate  --input req.md --output out/ --api-key sk-xxx
        """,
    )
    parser.add_argument("--task",
                        choices=["design", "implement", "test", "repair", "generate"],
                        default="generate",
                        help="任务类型: design|implement|test|repair|generate")
    parser.add_argument("--input", required=True, help="需求文档路径（Markdown 格式）")
    parser.add_argument("--output", default="output", help="输出目录（默认: output）")
    parser.add_argument("--api-key", default="", help="DeepSeek API 密钥（或设置环境变量 DEEPSEEK_API_KEY）")
    parser.add_argument("--base-url", default="", help="API 地址（或设置环境变量 DEEPSEEK_BASE_URL）")
    parser.add_argument("--max-repair", type=int, default=3, help="最大修复迭代次数（默认: 3）")

    args = parser.parse_args()

    # 命令行参数覆盖环境变量
    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
    if args.base_url:
        os.environ["DEEPSEEK_BASE_URL"] = args.base_url

    # 构建配置对象
    config = AgentConfig()
    config.output_dir = args.output
    config.max_repair_iterations = args.max_repair

    # 校验 API 密钥
    if not config.api_key:
        print("错误: 请设置 DEEPSEEK_API_KEY 环境变量或通过 --api-key 参数提供")
        sys.exit(1)

    # 读取需求文档
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

    # 统一通过 SEAgent 执行，task 参数控制流水线长度
    agent = SEAgent(config, task=args.task)
    agent.run(requirements)


if __name__ == "__main__":
    main()
