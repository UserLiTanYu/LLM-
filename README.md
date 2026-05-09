# LLM-Based Software Engineering Agent

基于大语言模型的软件工程智能体，支持 **需求分析 → 系统设计 → 代码实现 → 测试执行 → 自动修复** 的完整自动化流水线。

## 系统要求

- Python 3.11+
- DeepSeek API Key

## 快速开始

```bash
# 安装依赖
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 设置 API Key
export DEEPSEEK_API_KEY="sk-your-key"  # Windows: set DEEPSEEK_API_KEY=sk-your-key

# 运行完整流水线
python -m agent.main --task generate --input benchmarks/cases/case1_calculator/requirements.md --output output/
```

## CLI 命令

```bash
# 完整流水线（设计 + 实现 + 测试 + 修复）
python -m agent.main --task generate --input <需求文件.md> --output <输出目录>

# 仅设计阶段
python -m agent.main --task design --input <需求文件.md> --output <输出目录>

# 参数说明
python -m agent.main --help
```

## 项目结构

```
├── agent/                      # 智能体核心
│   ├── main.py                 # CLI入口
│   ├── orchestrator.py         # LangGraph工作流编排
│   ├── config.py               # 配置管理
│   ├── nodes/                  # 处理节点
│   │   ├── design.py           # 设计节点（需求→UML）
│   │   ├── implement.py        # 实现节点（设计→代码）
│   │   ├── test.py             # 测试节点（生成+执行）
│   │   └── repair.py           # 修复节点（定位+修复）
│   ├── tools/                  # 工具层
│   │   ├── file_manager.py     # 文件读写
│   │   ├── code_executor.py    # 代码执行沙箱
│   │   └── test_runner.py      # pytest测试运行器
│   └── llm/                    # LLM层
│       ├── gateway.py          # DeepSeek统一接口
│       └── prompts.py          # Prompt模板
├── benchmarks/                 # 基准测试用例
│   └── cases/
└── output/                     # 智能体输出目录
    ├── design/                 # 设计文档 + UML图
    ├── src/                    # 生成的代码
    └── tests/                  # 生成的测试
```

## 工作流程

```
需求文档(.md)
    │
    ▼
[Design Node]  ──→ 设计文档 + Mermaid类图 + 活动图
    │
    ▼
[Implement Node] ──→ Python代码
    │
    ▼
[Test Node]       ──→ pytest测试 + 执行
    │
    ├── 通过 ──→ 输出结果
    │
    └── 失败 ──→ [Repair Node] ──→ 修复代码 ──→ 重新测试（最多3次）
```
