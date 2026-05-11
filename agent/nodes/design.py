"""设计节点 — 调用 LLM 将需求文档转化为系统设计方案。

输出内容包括：
  1. architecture.md      — 架构设计文档（纯文字，不含图表代码）
  2. class_diagram.puml    — PlantUML 类图（核心实体及关系）
  3. activity_diagram.puml — PlantUML 活动图（核心业务流程）

_extract_plantuml() 辅助函数从 LLM 输出中逐块提取 PlantUML 代码，
分别保存为独立的 .puml 文件以便渲染。
architecture.md 中的 ```plantuml 块会被移除，避免重复。
"""

import re
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

    # 提取 PlantUML 图表，分别保存为独立 .puml 文件
    class_diagram = _extract_plantuml(design_output, "class")
    activity_diagram = _extract_plantuml(design_output, "start")

    if class_diagram:
        fm.write("design/class_diagram.puml", class_diagram)
    if activity_diagram:
        fm.write("design/activity_diagram.puml", activity_diagram)

    # 架构文档：移除所有 ```plantuml 代码块，只保留纯文字架构设计
    arch_text = _strip_plantuml_blocks(design_output)
    fm.write("design/architecture.md", arch_text)

    print("[Design] 设计方案已生成 → design/")
    return {"design": arch_text, "design_raw": design_output}


def _strip_plantuml_blocks(text: str) -> str:
    """移除文本中所有 ```plantuml ... ``` 代码块及关联的章节标题。

    先删除代码块，再清理留下的空标题行（如 "## 类图（PlantUML）" 等）。

    参数:
      text: 包含 PlantUML 代码块的 Markdown 文本

    返回:
      清理后的纯文字架构文档
    """
    # 删除所有 ```plantuml ... ``` 代码块
    text = re.sub(r"```plantuml\s*\n.*?```\n?", "", text, flags=re.DOTALL)
    # 删除图表相关的章节标题（含"类图""活动图""PlantUML""UML"等关键词）
    text = re.sub(r"^##\s.*?(?:类图|活动图|PlantUML|UML|时序图|状态图|组件图|部署图).*?\n+", "", text, flags=re.MULTILINE)
    # 删除紧邻的连续分隔线（---）和其后描述图表的过渡句（如"该活动图描述了..."）
    text = re.sub(r"\n---\n---\n.*?(?:图|流程|业务|描述).*", "", text, flags=re.DOTALL)
    text = re.sub(r"\n---\n.*?(?:图|流程|业务|描述).*", "", text, flags=re.DOTALL)
    # 去除 LLM 开场白：删除第一个 ## 标题前的对话性文字
    text = re.sub(r"^.*?(?=##\s)", "", text, flags=re.DOTALL)
    return text.strip()


def _extract_plantuml(text: str, diagram_keyword: str) -> str | None:
    """从 Markdown 文本中提取指定类型的 PlantUML 代码块。

    逐块匹配每个 ```plantuml ... ``` 代码块，独立提取其中的
    @startuml/@enduml 内容，根据 diagram_keyword 区分图类型。

    参数:
      text:            包含 PlantUML 代码的 Markdown 文本
      diagram_keyword: 图类型关键字（"class" 匹配类图、"start" 匹配活动图）

    返回:
      PlantUML 代码文本（@startuml ... @enduml），或 None（未找到）
    """
    # 先找到每个 ```plantuml ... ``` 块（不跨越块边界）
    blocks = re.findall(r"```plantuml\s*\n(.*?)```", text, re.DOTALL)

    for block in blocks:
        # 在每个独立块中提取 @startuml ... @enduml 内容
        match = re.search(rf"(@startuml.*?{diagram_keyword}.*?@enduml)", block, re.DOTALL)
        if match:
            return match.group(1).strip()

    return None
