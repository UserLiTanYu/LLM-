# LLM-Based Software Engineering Agent

基于大语言模型的软件工程智能体，覆盖 **需求分析 → 系统设计 → 代码实现 → 测试执行 → 自动修复** 全流程。课程项目，满足"分析+设计+实现+测试"四阶段连续覆盖。

## 安装


把下面**三行**粘贴到终端执行：

```powershell
# PowerShell — 克隆并运行本地安装脚本
git clone https://github.com/UserLiTanYu/LLM-.git
cd LLM-
.\install.ps1
```

```cmd
# cmd — 克隆并运行本地安装脚本
git clone https://github.com/UserLiTanYu/LLM-.git
cd LLM-
install.cmd
```


> **注意**：如果你在国内且 `git clone` 速度慢，可以使用镜像加速：
> ```powershell
> git clone https://ghproxy.com/https://github.com/UserLiTanYu/LLM-.git
> ```


## 使用

### 任务模式

| 模式 | 执行阶段 | 说明 |
|------|---------|------|
| `design` | 需求分析 → 系统设计 | 生成架构文档和 PlantUML 图表 |
| `implement` | 需求分析 → 系统设计 → 代码实现 | 生成 Python 代码 |
| `test` | 需求分析 → … → 测试执行 | 运行测试但不进修复循环 |
| `repair` | 需求分析 → … → 自动修复 | 全流程，测试失败自动修 Bug |
| `generate` | 同 `repair` | 全流程（默认） |

### PowerShell

```powershell
# 设置密钥（每次新开终端执行一次）
$env:DEEPSEEK_API_KEY = "sk-your-key"

# 仅设计阶段
se-agent --task design --input requirements.md --output output/

# 设计 + 代码实现
se-agent --task implement --input requirements.md --output output/

# 设计 + 实现 + 测试（不进修复循环）
se-agent --task test --input requirements.md --output output/

# 完整流水线（含自动修复）
se-agent --task generate --input requirements.md --output output/

# 指定密钥和最大修复次数
se-agent --task generate --input req.md --output out/ --api-key sk-xxx --max-repair 5
```

### CMD

```cmd
:: 设置密钥（每次新开终端执行一次）
set DEEPSEEK_API_KEY=sk-your-key

:: 仅设计阶段
se-agent --task design --input requirements.md --output output/

:: 设计 + 代码实现
se-agent --task implement --input requirements.md --output output/

:: 设计 + 实现 + 测试（不进修复循环）
se-agent --task test --input requirements.md --output output/

:: 完整流水线（含自动修复）
se-agent --task generate --input requirements.md --output output/

:: 指定密钥和最大修复次数
se-agent --task generate --input req.md --output out/ --api-key sk-xxx --max-repair 5
```

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
