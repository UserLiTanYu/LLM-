import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    """Agent configuration, loaded from environment variables."""

    # DeepSeek LLM
    model: str = "deepseek-chat"
    api_key: str = field(default_factory=lambda: os.environ.get("DEEPSEEK_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))

    # Limits
    max_repair_iterations: int = 3
    max_tokens_per_request: int = 8000
    temperature: float = 0.3

    # Paths
    output_dir: str = "output"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        return cls()
