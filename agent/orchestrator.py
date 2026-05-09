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
    requirements: str
    design: str
    code_output: str
    code_files: dict
    test_output: str
    test_results: dict
    test_passed: bool
    repair_output: str
    iteration: int
    error: str


class SEAgent:
    """Software Engineering Agent orchestrating design → implement → test → repair loop."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = LLMGateway(config)
        self.fm = FileManager(config.output_dir)
        self.test_runner = TestRunner(config.output_dir)

    def run(self, requirements: str) -> dict:
        """Run the full pipeline. Returns final state."""
        print("=" * 60)
        print("软件工程智能体启动")
        print("=" * 60)

        graph = self._build_graph()
        app = graph.compile()

        initial_state: AgentState = {
            "requirements": requirements,
            "design": "",
            "code_output": "",
            "code_files": {},
            "test_output": "",
            "test_results": {},
            "test_passed": False,
            "repair_output": "",
            "iteration": 0,
            "error": "",
        }

        result = app.invoke(initial_state)
        self._print_summary(result)
        return result

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("design", self._design_node)
        workflow.add_node("implement", self._implement_node)
        workflow.add_node("test", self._test_node)
        workflow.add_node("repair", self._repair_node)

        # Set entry
        workflow.set_entry_point("design")

        # Define edges
        workflow.add_edge("design", "implement")
        workflow.add_edge("implement", "test")

        # Conditional branching after test
        workflow.add_conditional_edges(
            "test",
            self._should_repair,
            {"repair": "repair", "done": END}
        )

        # After repair, re-test
        workflow.add_edge("repair", "test")

        return workflow

    def _design_node(self, state: AgentState) -> AgentState:
        result = run_design_node(self.llm, state["requirements"], self.fm)
        state["design"] = result["design"]
        return state

    def _implement_node(self, state: AgentState) -> AgentState:
        result = run_implement_node(
            self.llm, state["requirements"], state["design"], self.fm
        )
        state["code_output"] = result["code_output"]
        state["code_files"] = result["code_files"]
        return state

    def _test_node(self, state: AgentState) -> AgentState:
        result = run_test_node(
            self.llm, state["requirements"], state["code_output"],
            self.fm, self.test_runner,
        )
        state["test_output"] = result["test_output"]
        state["test_results"] = result["test_results"]
        state["test_passed"] = result["test_passed"]
        return state

    def _repair_node(self, state: AgentState) -> AgentState:
        state["iteration"] += 1
        failures = state["test_results"].get("failures", [])
        result = run_repair_node(
            self.llm, state["code_output"], state["test_output"],
            failures, self.fm,
        )
        state["code_output"] = result["code_output"]
        state["code_files"] = result["code_files"]
        state["repair_output"] = result["repair_output"]
        return state

    def _should_repair(self, state: AgentState) -> str:
        if state["test_passed"]:
            return "done"
        if state["iteration"] >= self.config.max_repair_iterations:
            print(f"[Agent] 已达最大修复次数 ({self.config.max_repair_iterations})，停止修复")
            return "done"
        return "repair"

    def _print_summary(self, state: AgentState):
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
