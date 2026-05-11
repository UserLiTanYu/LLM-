# 基于大语言模型的软件工程智能体 — 项目规划

## 一、选题决策

### 功能组合：a（分析+设计）+ b（实现+测试）+ 修复闭环

**覆盖阶段：分析 → 设计 → 实现 → 测试 → 修复（完整四阶段 + 闭环）**

| 阶段 | 输入 | 输出 | 对应要求 |
|------|------|------|----------|
| 分析+设计 | 自然语言需求文档/PRD | ①架构设计文档 ②PlantUML类图 ③PlantUML活动图 | 组合a：至少两种UML图 |
| 实现 | 需求 + 设计模型 | 可运行的 Python 代码 | 组合b前半 |
| 测试 | 需求 + 代码 | pytest单元测试 + 执行结果报告 | 组合b后半 |
| 修复 | 测试失败信息 + 代码 | Bug定位 + 修复补丁 + 修复说明 | 额外加分项 |

**为什么选这个组合：**
- 覆盖 4 个连续阶段，远超最低要求（仅需2个），基础分更高
- 输出类图+活动图两种UML，满足组合a要求
- 实现→测试→修复 形成自动闭环，答辩演示效果好
- 与"AI代码助手"方向吻合，个人兴趣驱动

---

## 二、技术选型

| 层 | 选型 | 理由 |
|----|------|------|
| 编排框架 | **LangGraph** | 适合多阶段流水线，状态图建模，支持条件分支和循环 |
| LLM 工具层 | **LangChain** | 标准工具调用、Prompt模板 |
| 大模型 | **DeepSeek (deepseek-chat)** | OpenAI兼容SDK，代码能力强，成本低（¥1/百万token） |
| 代码执行沙箱 | **subprocess + venv** | 安全执行生成的Python代码和pytest |
| CLI 框架 | **argparse** | Python标准库，满足命令行启动要求 |
| IDE 集成 | **VS Code Extension (TypeScript)** | 满足课程要求，覆盖范围最广 |
| 测试框架 | **pytest** | 运行生成的测试用例，JSON报告输出 |
| 输出格式 | **PlantUML** (类图+活动图) + **Markdown** (文档) | 文本化、可版本管理 |
| 语言 | **Python**（智能体核心 + 生成目标代码）+ **TypeScript**（VS Code插件） | 智能体和生成代码同语言，降低复杂度 |

---

## 三、系统架构

```
┌──────────────────────────────────────────────┐
│                 CLI 入口                       │
│  ./agent --task generate --input req.md       │
│           --output ./output/                   │
└────────────────────┬─────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│            Agent Orchestrator                 │
│         (LangGraph StateGraph)                │
│                                                │
│  ┌──────────┐    ┌──────────┐    ┌─────────┐ │
│  │ Design   │───▶│ Implement│───▶│  Test   │ │
│  │ Node     │    │ Node     │    │  Node   │ │
│  └──────────┘    └──────────┘    └────┬────┘ │
│                                       │       │
│                          ┌────────────▼─────┐ │
│                          │   Test Passed?    │ │
│                          └───┬──────────┬───┘ │
│                              │ Yes      │ No  │
│                              ▼          ▼     │
│                          ┌──────┐ ┌──────────┐│
│                          │Output│ │  Repair  ││
│                          │ Node │ │  Node    ││
│                          └──────┘ └────┬─────┘│
│                                       │       │
│                          ┌────────────▼─────┐ │
│                          │ Re-test (loop)   │ │
│                          │ max 3 iterations │ │
│                          └──────────────────┘ │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              Tool Layer                        │
│  ┌──────────┬──────────┬──────────────┐      │
│  │Code      │Test      │ File I/O     │      │
│  │Executor  │Runner    │ (read/write) │      │
│  └──────────┴──────────┴──────────────┘      │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              LLM Gateway                       │
│  (Anthropic SDK / OpenAI SDK / 本地模型)       │
└──────────────────────────────────────────────┘
```

### VS Code 集成架构

```
┌─────────────────────────────────┐
│        VS Code Extension         │
│  ┌───────────────────────────┐  │
│  │ 右键菜单 + 命令面板触发     │  │
│  │ /agent.generateFromDoc    │  │
│  │ /agent.designFromPRD      │  │
│  └───────────┬───────────────┘  │
│              ▼                  │
│  ┌───────────────────────────┐  │
│  │ 调用本地 CLI Agent         │  │
│  │ spawn("./agent", args)    │  │
│  └───────────┬───────────────┘  │
│              ▼                  │
│  ┌───────────────────────────┐  │
│  │ 结果展示面板                │  │
│  │ (Webview Panel)           │  │
│  │ - 设计图 (PlantUML渲染)     │  │
│  │ - 代码文件 (Diff查看)      │  │
│  │ - 测试报告 (表格)          │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

---

## 四、核心模块设计

### 1. Orchestrator（编排器）
- LangGraph StateGraph 定义任务流程
- 状态对象跨节点传递：`{requirements, design, code, tests, test_results, iteration_count}`
- 条件边：根据测试结果决定走 Output 还是 Repair
- 最大修复迭代3次，超过则标记失败

### 2. Design Node（设计节点） — 对应组合a
- **输入**：自然语言需求文档/PRD
- **处理流程**：
  1. 需求分析：提取关键实体、行为、状态
  2. 架构设计：模块划分、职责分配、技术选型建议
  3. UML生成：PlantUML格式类图 + 活动图
- **输出**：
  - `design/architecture.md` — 架构设计说明
  - `design/class_diagram.puml` — 类图（至少包含实体类+关系）
  - `design/activity_diagram.puml` — 活动图（核心业务流程）
- **Prompt策略**：分两步走——先分析需求提取实体和流程，再生成UML图；输出格式用代码块标记约束
- **工具调用**：File Write（输出PlantUML文件）

### 3. Implement Node（实现节点）
- **输入**：需求 + 设计文档（类图+活动图）
- **处理流程**：先规划文件结构 → 逐文件生成代码 → 汇总检查
- **输出**：`src/` 目录下的Python代码文件
- **Prompt策略**：
  - System Prompt要求输出可运行Python代码
  - 约束：类型注解、PEP 8、docstring
  - Few-shot示例：1个完整的需求→代码对
- **工具调用**：File Write（写入.py文件）

### 4. Test Node（测试节点）
- **输入**：需求 + 生成的代码
- **处理流程**：读取代码 → 分析需要测试的方法 → 生成pytest用例 → 执行测试
- **输出**：`tests/` 目录下的pytest文件 + `test_results.json`
- **Prompt策略**：要求覆盖正常路径+边界+异常，使用pytest fixture
- **工具调用**：File Write → subprocess 执行 `pytest --json-report` → 解析结果

### 5. Repair Node（修复节点）
- 输入：代码 + 失败测试 + 错误日志
- Prompt 策略：错误定位 → 根因分析 → 生成修复补丁
- 工具调用：File Read/Write
- 输出：修复后的代码 + 修复说明

### 6. LLM Gateway（大模型网关）
- **统一接口**：`openai` Python SDK 调用 DeepSeek API（兼容格式）
- **配置**：`DEEPSEEK_API_KEY` + `DEEPSEEK_BASE_URL`（默认 https://api.deepseek.com）
- **流式输出**：SSE解析，CLI实时打印进度
- **重试机制**：API调用失败自动重试3次（exponential backoff）
- **Token统计**：每次调用记录输入/输出token，汇总报告中展示

### 7. VS Code Extension
- 命令注册：`agent.generate` / `agent.design` / `agent.test`
- 右键菜单：在.md文件上右键触发"生成代码"
- Webview Panel：展示PlantUML图 + 代码Diff + 测试报告
- 调用方式：spawn CLI进程，通过stdout JSON-lines获取进度

---

## 五、执行计划（按课程里程碑）

### 第1周：选题确认 + 环境搭建
- [ ] 确认功能组合（a+b：分析+设计+实现+测试+修复闭环）
- [ ] 申请 DeepSeek API Key，充值测试额度
- [ ] 搭建 Python 项目骨架（pip + venv + 目录结构）
- [ ] 配置 LangGraph + LangChain + openai SDK
- [ ] 编写 README.md 说明项目目标和结构

### 第2-3周：核心引擎开发
- [ ] 实现 LLM Gateway（统一调用接口）
- [ ] 实现 Design Node（需求→设计文档+PlantUML图）
- [ ] 实现 Implement Node（设计→代码）
- [ ] 实现 Test Node（代码→测试用例+执行）
- [ ] 实现 Repair Node（失败→修复）
- [ ] 实现 Orchestrator（LangGraph工作流串联）

### 第4-5周：CLI + 基准测试构建
- [ ] 实现 CLI 入口（argparse，支持所有参数）
- [ ] 构建基准测试集（5+场景，覆盖不同难度）
- [ ] 执行基准测试，收集成功率数据
- [ ] 迭代优化 Prompt 和修复策略

### 第6周：IDE集成
- [ ] 搭建 VS Code Extension 骨架
- [ ] 实现命令注册 + 右键菜单
- [ ] 实现 Webview 结果展示面板
- [ ] 端到端联调（IDE触发→CLI执行→结果展示）

### 第7周：文档编写
- [ ] 智能体工作原理技术报告
- [ ] 系统设计方案文档
- [ ] 测试方案与测试报告
- [ ] 使用说明 + 2个完整应用案例

### 第8周：最终交付
- [ ] 所有文档转PDF
- [ ] 录制演示视频
- [ ] Git仓库整理 + 最终检查

---

## 六、基准测试设计（5个场景）

| 编号 | 场景 | 输入 | 期望输出（Python） | 难度 |
|------|------|------|----------|------|
| 1 | 计算器模块 | PRD：四则运算计算器 | calculator.py (Calculator类) + test_calculator.py | 简单 |
| 2 | 用户管理系统 | PRD：CRUD用户管理 | user_service.py + user.py (Model) + test_user_service.py | 中等 |
| 3 | 订单状态机 | PRD：订单生命周期 | order.py (状态模式) + test_order.py (6种状态转换) | 中等 |
| 4 | 任务调度器 | PRD：并发任务队列 | scheduler.py (多线程) + test_scheduler.py (并发测试) | 困难 |
| 5 | REST API服务 | PRD：TODO API | FastAPI应用 + test_api.py (httpx集成测试) | 困难 |

每个场景度量：代码可运行率、测试通过率、修复成功率、修复迭代次数、Token消耗

每个场景度量：代码可运行率、测试通过率、修复成功率、迭代次数

---

## 七、目录结构

```
llm-se-agent/
├── README.md
├── requirements.txt
├── agent/                      # 智能体核心
│   ├── __init__.py
│   ├── main.py                 # CLI入口
│   ├── orchestrator.py         # LangGraph工作流
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── design.py           # 设计节点
│   │   ├── implement.py        # 实现节点
│   │   ├── test.py             # 测试节点
│   │   └── repair.py           # 修复节点
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── code_executor.py    # 代码执行沙箱
│   │   ├── file_manager.py     # 文件读写
│   │   └── test_runner.py      # 测试运行器
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gateway.py          # LLM统一接口
│   │   └── prompts.py          # Prompt模板
│   └── config.py               # 配置管理
├── benchmarks/                 # 基准测试
│   ├── cases/
│   │   ├── case1_calculator/
│   │   │   ├── requirements.md
│   │   │   └── expected/       # 期望输出（人工编写）
│   │   ├── case2_user_mgmt/
│   │   └── ...                 # 共5个case
│   └── run_benchmark.py
├── vscode-extension/           # VS Code插件
│   ├── package.json
│   ├── src/
│   │   ├── extension.ts
│   │   ├── commands.ts
│   │   └── webview/
│   │       └── panel.ts
│   └── tsconfig.json
├── docs/                       # 文档源文件（Markdown）
│   ├── tech-report.md
│   ├── design-doc.md
│   ├── test-report.md
│   └── user-guide.md
└── output/                     # 智能体输出目录
```

---

## 八、关键技术决策说明

### 为什么用 LangGraph 而不是 CrewAI？
- LangGraph 的状态图模型天然适合"设计→实现→测试→修复"线性+条件分支流程
- 比 CrewAI 更底层，自定义程度更高，能体现"自主实现"部分
- 课程要求说明哪些是自主实现、哪些由框架提供，LangGraph 边界清晰

### 为什么 CLI + VS Code Extension 双层？
- CLI 满足课程"命令行启动"要求
- VS Code Extension 满足 IDE 集成要求
- Extension 内部调 CLI，共用核心逻辑，不重复开发

### Prompt 工程策略
- System Prompt：定义角色 + 输出格式约束
- Few-shot Examples：每个节点提供2-3个输入输出示例
- Chain of Thought：要求LLM先分析再生成
- 结构化输出：使用 JSON Schema 或 Markdown 格式标记约束输出
- 错误反馈：Repair节点将编译错误/测试失败信息作为负面示例嵌入Prompt

---

## 九、验证方式

1. **基准测试**：`python benchmarks/run_benchmark.py`，输出每个场景的通过率报告
2. **CLI测试**：
   ```bash
   # 完整流水线：需求 → 设计 + 代码 + 测试
   export DEEPSEEK_API_KEY="sk-xxx"
   python -m agent.main --task generate --input benchmarks/cases/case1_calculator/requirements.md --output output/
   ```
3. **IDE集成测试**：在VS Code中打开需求文件，右键触发"AI Agent: Generate"，验证结果面板展示PlantUML图+代码+测试报告
4. **端到端测试**：从需求文档到可运行代码+测试通过的完整流程
5. **修复闭环测试**：故意在基准测试中引入Bug代码，验证Repair节点能定位并修复

## 十、DeepSeek API 对接要点

- **SDK**：`pip install openai`（DeepSeek兼容OpenAI格式）
- **调用方式**：
  ```python
  from openai import OpenAI
  client = OpenAI(api_key="sk-xxx", base_url="https://api.deepseek.com")
  response = client.chat.completions.create(
      model="deepseek-chat",
      messages=[...],
      stream=True  # 流式输出
  )
  ```
- **模型选择**：`deepseek-chat`（通用对话模型，代码能力足够）
- **上下文窗口**：64K tokens，足够容纳需求+设计+代码+测试
- **成本控制**：约¥1/百万输入token，单次完整流水线约消耗5000-20000 token（¥0.005-0.02），开发测试阶段成本可忽略
