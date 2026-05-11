# LLM-Based Software Engineering Agent

基于大语言模型的软件工程智能体，覆盖 **需求分析 → 系统设计 → 代码实现 → 测试执行 → 自动修复** 全流程。课程项目，满足"分析+设计+实现+测试"四阶段连续覆盖。

## 安装

### 一键安装（推荐）

**把下面这行粘贴到终端执行即可**，脚本自动完成：克隆仓库 → 创建虚拟环境 → 安装依赖 → 注册 `se-agent` 命令 → 激活环境。

```powershell
# PowerShell（iex 在内存中执行，无需创建临时文件）
iex ((curl.exe -fsSL https://raw.githubusercontent.com/UserLiTanYu/LLM-/main/install.ps1) -join "`n")
```

```cmd
:: CMD
curl -fsSL https://raw.githubusercontent.com/UserLiTanYu/LLM-/main/install.cmd -o install.cmd && install.cmd && del install.cmd
```

### 手动安装

```powershell
git clone https://github.com/UserLiTanYu/LLM-.git
cd LLM-
python -m venv venv
venv\Scripts\activate
pip install -e .
```

## 使用

### PowerShell

```powershell
# 设置密钥（每次新开终端执行一次）
$env:DEEPSEEK_API_KEY = "sk-your-key"

# 完整流水线
se-agent --task generate --input 需求文档.md --output output/

# 仅设计阶段
se-agent --task design --input 需求文档.md --output output/

# 指定密钥和最大修复次数
se-agent --task generate --input req.md --output out/ --api-key sk-xxx --max-repair 5
```

### CMD

```cmd
:: 设置密钥（每次新开终端执行一次）
set DEEPSEEK_API_KEY=sk-your-key

:: 完整流水线
se-agent --task generate --input 需求文档.md --output output/

:: 仅设计阶段
se-agent --task design --input 需求文档.md --output output/

:: 指定密钥和最大修复次数
se-agent --task generate --input req.md --output out/ --api-key sk-xxx --max-repair 5
```

## 基准测试结果

| 场景 | 用例数 | 通过 | 修复迭代 | 结果 |
|------|--------|------|----------|------|
| 计算器模块 | 53 | 51 | 3轮 | 96.2% |

**剩余 2 个失败分析**：均为测试生成偏差——浮点精度比较未用 `pytest.approx`、边界用例与需求矛盾（期望除以零返回 ∞ 而非抛异常），属测试生成质量问题而非代码 Bug。

## 项目结构

```
├── agent/                      # 智能体核心
│   ├── main.py                 # CLI入口 → se-agent 命令
│   ├── orchestrator.py         # LangGraph 工作流编排
│   ├── config.py               # 配置管理
│   ├── nodes/                  # 处理节点
│   │   ├── design.py           # 设计节点（需求→UML类图+活动图）
│   │   ├── implement.py        # 实现节点（设计→Python代码）
│   │   ├── test.py             # 测试节点（生成pytest+执行）
│   │   └── repair.py           # 修复节点（失败→定位+修复）
│   ├── tools/                  # 工具层
│   │   ├── file_manager.py     # 文件读写 + 代码块解析
│   │   ├── code_executor.py    # 代码执行沙箱
│   │   └── test_runner.py      # pytest运行器
│   └── llm/                    # LLM层
│       ├── gateway.py          # DeepSeek统一接口（流式+重试）
│       └── prompts.py          # 四阶段 System Prompt 模板
├── benchmarks/                 # 基准测试用例
├── install.cmd                 # Windows 一键安装脚本
├── pyproject.toml              # 包配置（定义 se-agent 命令）
└── requirements.txt            # 依赖清单
```

## 工作流程

```
需求文档(.md)
    │
    ▼
[Design Node]        → design/architecture.md + class_diagram.puml + activity_diagram.puml
    │
    ▼
[Implement Node]     → src/*.py
    │
    ▼
[Test Node]          → tests/*.py → pytest → 测试报告
    │
    ├── 全部通过 → 完成
    │
    └── 有失败 → [Repair Node] → 修复代码 → 重新测试（默认最多3次）
```

## 技术栈

| 层 | 技术 |
|----|------|
| 编排引擎 | LangGraph（状态图驱动） |
| LLM 接入 | DeepSeek（OpenAI 兼容 SDK） |
| 目标语言 | Python 3.11+ |
| 测试框架 | pytest + pytest-json-report |
| IDE 集成 | VS Code Extension（规划中） |
