"""编排模块 — LangGraph 工作流引擎，串联设计→实现→测试→修复全流程。

核心组件：
  AgentState:  工作流中的状态对象，在各个节点间传递
  SEAgent:     软件工程智能体，构建并执行 LangGraph 有向图

工作流拓扑：
  design ──→ implement ──→ test ──┬── (测试通过) ──→ END
                                   │
                                   ├── (超过最大重试) ──→ END
                                   │
                                   └── (失败且可重试) ──→ repair ──→ test（循环）

修复循环会在以下条件终止：
  1. 所有测试通过
  2. 修复次数达到 max_repair_iterations 上限
"""

from typing import TypedDict

from langgraph.graph import StateGraph, END

from agent.config import AgentConfig
from agent.llm.gateway import LLMGateway
from agent.tools.file_manager import FileManager
from agent.tools.test_runner import TestRunner
from agent.nodes.design import run_design_node
from agent.nodes.implement import run_implement_node
from agent.nodes.test import run_test_node
from agent.nodes.repair import run_repair_node


class AgentState(TypedDict):
    """工作流状态 — 在 LangGraph 各节点间流转的共享字典。

    每个节点读取需要的字段，更新自己负责的字段后返回。
    """
    requirements: str      # 原始需求文档内容
    design: str            # LLM 生成的设计方案（纯文字 Markdown）
    design_raw: str        # LLM 生成的原始设计方案（含 PlantUML 图表）
    code_output: str       # LLM 生成的代码（原始文本）
    code_files: dict       # 解析后的代码文件 {文件名: 内容}
    test_output: str       # LLM 生成的测试代码（原始文本）
    test_results: dict     # pytest 运行结果摘要
    test_passed: bool      # 测试是否全部通过
    repair_output: str     # LLM 生成的修复方案
    iteration: int         # 当前修复迭代次数
    error: str             # 异常信息（如果有）


class SEAgent:
    """软件工程智能体 — 编排 设计→实现→测试→修复 的完整循环。

    使用 LangGraph 的 StateGraph 构建工作流：
    - 4 个处理节点：design、implement、test、repair
    - 条件边：测试失败且未超限时进入修复循环
    """

    def __init__(self, config: AgentConfig):
        """初始化智能体，创建 LLM 网关、文件管理器和测试运行器。"""
        self.config = config
        self.llm = LLMGateway(config)
        self.fm = FileManager(config.output_dir)
        self.test_runner = TestRunner(config.output_dir)

    def run(self, requirements: str) -> dict:
        """运行完整流水线，返回最终状态字典。"""
        print("=" * 60)
        print("软件工程智能体启动")
        print("=" * 60)

        # 构建并编译 LangGraph 工作流
        graph = self._build_graph()
        app = graph.compile()

        # 构造初始状态（所有字段初始化为空/零值）
        initial_state: AgentState = {
            "requirements": requirements,
            "design": "",
            "design_raw": "",
            "code_output": "",
            "code_files": {},
            "test_output": "",
            "test_results": {},
            "test_passed": False,
            "repair_output": "",
            "iteration": 0,
            "error": "",
        }

        # 执行工作流
        result = app.invoke(initial_state)
        self._print_summary(result)
        return result

    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 有向图，定义节点和边。

        返回包含以下结构的 StateGraph：
          design → implement → test → [条件分支] → repair → test（循环）
        """
        workflow = StateGraph(AgentState)

        # 注册四个处理节点
        workflow.add_node("design", self._design_node)        # 方案设计
        workflow.add_node("implement", self._implement_node)  # 代码生成
        workflow.add_node("test", self._test_node)             # 测试生成与执行
        workflow.add_node("repair", self._repair_node)         # 自动修复

        # 设置入口节点
        workflow.set_entry_point("design")

        # 定义顺序边：design → implement → test
        workflow.add_edge("design", "implement")
        workflow.add_edge("implement", "test")

        # 测试后的条件分支：通过/超限 → END，失败 → repair
        workflow.add_conditional_edges(
            "test",
            self._should_repair,
            {"repair": "repair", "done": END}
        )

        # 修复后重新测试
        workflow.add_edge("repair", "test")

        return workflow

    def _design_node(self, state: AgentState) -> AgentState:
        """设计节点 — 调用 LLM 生成架构设计和 PlantUML 图表。"""
        result = run_design_node(self.llm, state["requirements"], self.fm)
        state["design"] = result["design"]
        state["design_raw"] = result["design_raw"]
        return state

    def _implement_node(self, state: AgentState) -> AgentState:
        """实现节点 — 根据需求和设计方案生成 Python 代码。"""
        result = run_implement_node(
            self.llm, state["requirements"], state["design_raw"], self.fm
        )
        state["code_output"] = result["code_output"]
        state["code_files"] = result["code_files"]
        return state

    def _test_node(self, state: AgentState) -> AgentState:
        """测试节点 — 生成 pytest 用例并执行，返回测试结果。"""
        result = run_test_node(
            self.llm, state["requirements"], state["code_output"],
            self.fm, self.test_runner,
        )
        state["test_output"] = result["test_output"]
        state["test_results"] = result["test_results"]
        state["test_passed"] = result["test_passed"]
        return state

    def _repair_node(self, state: AgentState) -> AgentState:
        """修复节点 — 分析失败测试，定位 Bug 并修复代码。"""
        state["iteration"] += 1  # 递增修复计数
        failures = state["test_results"].get("failures", [])
        result = run_repair_node(
            self.llm, state["code_output"], state["test_output"],
            failures, self.fm, state["design_raw"],
        )
        state["code_output"] = result["code_output"]
        state["code_files"] = result["code_files"]
        state["repair_output"] = result["repair_output"]
        return state

    def _should_repair(self, state: AgentState) -> str:
        """条件判断函数 — 决定测试后是结束还是进入修复循环。

        返回 "done" 的情况:
          1. 所有测试通过
          2. 已达到最大修复次数

        返回 "repair" 的情况:
          测试失败且还有修复次数剩余
        """
        if state["test_passed"]:
            return "done"
        if state["iteration"] >= self.config.max_repair_iterations:
            print(f"[Agent] 已达最大修复次数 ({self.config.max_repair_iterations})，停止修复")
            return "done"
        return "repair"

    def _print_summary(self, state: AgentState):
        """打印流水线执行摘要。"""
        print("\n" + "=" * 60)
        print("执行摘要")
        print("=" * 60)
        print(f"  设计文档: design/architecture.md")
        print(f"  生成代码: src/ ({len(state['code_files'])} 个文件)")
        print(f"  测试文件: tests/")
        tr = state["test_results"]
        print(f"  测试结果: 通过 {tr.get('passed', 0)}, 失败 {tr.get('failed', 0)}")
        print(f"  修复次数: {state['iteration']}")
        print(f"  Token消耗: {self.llm.token_usage}")
        print(f"  结论: {'测试通过' if state['test_passed'] else '存在未修复的失败'}")
