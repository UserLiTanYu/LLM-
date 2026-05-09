from agent.llm.gateway import LLMGateway
from agent.llm.prompts import DESIGN_SYSTEM
from agent.tools.file_manager import FileManager


def run_design_node(llm: LLMGateway, requirements: str, fm: FileManager) -> dict:
    """Generate system design from requirements. Returns state update dict."""
    print("[Design] 分析需求，生成设计方案...")

    messages = [
        {"role": "system", "content": DESIGN_SYSTEM},
        {"role": "user", "content": f"请根据以下需求文档生成系统设计方案：\n\n{requirements}"},
    ]

    design_output = llm.chat(messages)

    # Save outputs
    fm.write("design/architecture.md", design_output)

    # Extract and save Mermaid diagrams separately
    class_diagram = _extract_mermaid(design_output, "classDiagram")
    activity_diagram = _extract_mermaid(design_output, "flowchart")

    if class_diagram:
        fm.write("design/class_diagram.mmd", class_diagram)
    if activity_diagram:
        fm.write("design/activity_diagram.mmd", activity_diagram)

    print("[Design] 设计方案已生成 → design/")
    return {"design": design_output}


def _extract_mermaid(text: str, diagram_type: str) -> str | None:
    """Extract a Mermaid diagram block from markdown text."""
    import re
    # Match ```mermaid ... ``` blocks containing the diagram type
    pattern = rf"```mermaid\s*\n(.*?{diagram_type}.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
