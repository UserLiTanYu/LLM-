"""配置模块 — 集中管理智能体的所有配置项。

所有配置通过环境变量和 dataclass 的默认值提供，
支持命令行参数覆写。

环境变量：
  DEEPSEEK_API_KEY   DeepSeek API 密钥（必须）
  DEEPSEEK_BASE_URL  API 地址（默认 https://api.deepseek.com）
"""

import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """智能体配置类，从环境变量加载默认值。"""

    # ---- DeepSeek LLM 配置 ----
    model: str = "deepseek-chat"
    api_key: str = field(default_factory=lambda: os.environ.get("DEEPSEEK_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))

    # ---- 限制参数 ----
    max_repair_iterations: int = 3      # 测试失败后的最大自动修复次数
    max_tokens_per_request: int = 8000  # 每次 LLM 请求的最大输出 token
    temperature: float = 0.3            # LLM 采样温度（越低越确定）

    # ---- 路径 ----
    output_dir: str = "output"          # 所有生成文件的输出根目录

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """从当前环境变量创建配置实例。"""
        return cls()
