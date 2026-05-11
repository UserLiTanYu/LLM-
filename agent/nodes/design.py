"""设计节点 — 调用 LLM 将需求文档转化为系统设计方案。

输出内容包括：
  1. architecture.md      — 架构设计文档（Markdown）
  2. class_diagram.puml    — PlantUML 类图（核心实体及关系）
  3. activity_diagram.puml — PlantUML 活动图（核心业务流程）

_extract_plantuml() 辅助函数从 LLM 输出中提取 PlantUML 代码块，
分别保存为独立的 .puml 文件以便渲染。
"""

from agent.llm.gateway import LLMGateway
from agent.llm.prompts import DESIGN_SYSTEM
from agent.tools.file_manager import FileManager


def run_design_node(llm: LLMGateway, requirements: str, fm: FileManager) -> dict:
    """根据需求生成系统设计方案。返回状态更新字典。

    参数:
      llm:          LLM 网关实例
      requirements: 需求文档原始文本
      fm:           文件管理器（用于保存输出）

    返回:
      {"design": 设计方案全文（Markdown）}
    """
    print("[Design] 分析需求，生成设计方案...")

    messages = [
        {"role": "system", "content": DESIGN_SYSTEM},
        {"role": "user", "content": f"请根据以下需求文档生成系统设计方案：\n\n{requirements}"},
    ]

    # 调用 LLM 生成设计方案
    design_output = llm.chat(messages)

    # 保存完整的架构设计文档
    fm.write("design/architecture.md", design_output)

    # 从输出中提取 PlantUML 图表，分别保存以便独立渲染
    class_diagram = _extract_plantuml(design_output, "class")
    activity_diagram = _extract_plantuml(design_output, "start")

    if class_diagram:
        fm.write("design/class_diagram.puml", class_diagram)
    if activity_diagram:
        fm.write("design/activity_diagram.puml", activity_diagram)

    print("[Design] 设计方案已生成 → design/")
    return {"design": design_output}


def _extract_plantuml(text: str, diagram_keyword: str) -> str | None:
    """从 Markdown 文本中提取指定类型的 PlantUML 代码块。

    匹配 ```plantuml ... ``` 包裹的代码块，
    返回包含 diagram_keyword 关键字的 @startuml/@enduml 内容。
    例如：_extract_plantuml(text, "class") 提取类图代码，
         _extract_plantuml(text, "start") 提取活动图代码。

    参数:
      text:            包含 PlantUML 代码的 Markdown 文本
      diagram_keyword: 图类型关键字（如 "class" 匹配类图、"start" 匹配活动图）

    返回:
      PlantUML 代码文本（@startuml ... @enduml），或 None（未找到）
    """
    import re
    # 匹配 ```plantuml ... ``` 包裹的代码块，提取从 @startuml 到 @enduml 之间的内容
    pattern = rf"```plantuml\s*\n(.*?@startuml.*?{diagram_keyword}.*?@enduml.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
