# 项目执行流程介绍

## 概览

这是一个 **LLM 驱动的软件工程智能体**，能根据需求文档**自动完成**完整的软件开发流程。技术栈为：**LangGraph**（工作流编排）+ **DeepSeek**（大模型）+ **pytest**（测试执行）。

## 整体架构

```
agent/
├── main.py              ← CLI 命令行入口
├── config.py            ← 配置管理（模型、路径、限制参数）
├── orchestrator.py      ← 核心编排器（LangGraph 工作流引擎）
├── llm/
│   ├── gateway.py       ← LLM 网关（封装 DeepSeek API 调用）
│   └── prompts.py       ← 四个角色的 System Prompt
├── nodes/
│   ├── design.py        ← 设计节点（生成架构方案+PlantUML图）
│   ├── implement.py     ← 实现节点（生成 Python 代码）
│   ├── test.py          ← 测试节点（生成+执行 pytest）
│   └── repair.py        ← 修复节点（分析失败+自动修Bug）
└── tools/
    ├── file_manager.py  ← 文件读写工具
    ├── code_executor.py ← 代码沙箱执行器
    └── test_runner.py   ← pytest 封装与结果解析
```

## 执行流程（4+1 阶段）

启动方式：`se-agent --task generate --input requirements.md --output output/`

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph 工作流                          │
│                                                              │
│   ① DESIGN         ② IMPLEMENT       ③ TEST                │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐            │
│  │ 需求分析  │───→│ 代码生成   │───→│ 测试验证   │──┬── 通过 → END
│  │ 架构设计  │    │ 文件写入   │    │ pytest执行 │  │         │
│  │ PlantUML图│    │ src/      │    │ tests/     │  │ 超限 → END
│  └──────────┘    └───────────┘    └───────────┘  │         │
│                                                   │ 失败     │
│                                            ┌──────┘         │
│                                            ↓                │
│                                     ④ REPAIR                │
│                                    ┌──────────┐             │
│                                    │ Bug定位   │──────┘     │
│                                    │ 代码覆盖  │  循环重测   │
│                                    └──────────┘             │
└─────────────────────────────────────────────────────────────┘
```

### ① 设计阶段（Design Node）— [agent/nodes/design.py](agent/nodes/design.py)

- 将需求文档发送给 LLM（角色：资深软件架构师）
- 生成 `design/architecture.md`（架构文档）、`design/class_diagram.puml`（类图）、`design/activity_diagram.puml`（活动图）
- PlantUML 图用正则从输出中提取，单独保存以便渲染

### ② 实现阶段（Implement Node）— [agent/nodes/implement.py](agent/nodes/implement.py)

- 将需求 + 设计方案发送给 LLM（角色：资深 Python 开发）
- LLM 按要求输出带类型注解、PEP8、docstring 的代码
- 用正则解析 ` ```python:filename.py ``` ` 格式的代码块，逐个写入 `src/` 目录

### ③ 测试阶段（Test Node）— [agent/nodes/test.py](agent/nodes/test.py)

- 将需求 + 实现代码发送给 LLM（角色：资深测试工程师）
- 生成覆盖正常路径、边界条件、异常的 pytest 用例
- **实际执行 pytest**，通过 `pytest-json-report` 收集结构化结果（通过/失败数、失败详情）

### ④ 修复阶段（Repair Node）— [agent/nodes/repair.py](agent/nodes/repair.py)

- 仅在测试失败且未超过最大修复次数时触发（默认最多3次）
- 将代码 + 测试 + 失败详情发送给 LLM（角色：资深调试工程师）
- LLM 定位 Bug 根因并输出修复后代码，覆盖 `src/` 中的文件
- 修复后**回到测试节点**重新执行，形成循环直到全部通过或达到上限

## 关键技术细节

| 要点 | 说明 |
|------|------|
| **LLM 调用** | 通过 OpenAI 兼容 SDK 调用 DeepSeek，内置 3 次指数退避重试 |
| **代码解析** | 正则匹配代码块，优先 `python:filename.py` 格式，回退 `python` 格式 |
| **测试执行** | 子进程运行 pytest，自动将 `src/` 加入 `PYTHONPATH`，60s 超时保护 |
| **输出结构** | `output/design/`（设计文档）、`output/src/`（生成代码）、`output/tests/`（测试代码） |
| **Token 统计** | 每次 LLM 调用自动累计 input/output token 数，结束时统一输出 |
| **两种模式** | `--task generate` 完整流水线 / `--task design` 仅设计方案 |

## 模块间数据流

```
CLI (main.py)
  │  解析参数、读取需求文档
  │  创建 AgentConfig
  ▼
SEAgent (orchestrator.py)
  │  初始化 LLMGateway、FileManager、TestRunner
  │  构建 LangGraph 有向图
  ▼
AgentState (TypedDict)
  │  在 4 个节点间流转的共享状态字典
  │  包含: requirements → design → code → test → repair
  ▼
LLMGateway (gateway.py)
  │  封装 OpenAI SDK → DeepSeek API
  │  指数退避重试、Token 统计
  ▼
各 Node (nodes/*.py)
  │  调用 LLM → 解析输出 → 写入文件
  │  返回状态更新字典，交由 LangGraph 路由
  ▼
FileManager + TestRunner (tools/*.py)
  │  文件读写、pytest 执行与结果解析
  ▼
输出目录 (output/)
  ├── design/   (架构文档 + PlantUML 图表)
  ├── src/      (生成的 Python 代码)
  └── tests/    (生成的 pytest 用例)
```
