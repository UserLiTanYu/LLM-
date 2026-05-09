import time
from openai import OpenAI
from agent.config import AgentConfig


class LLMGateway:
    """Unified LLM interface for DeepSeek API (OpenAI-compatible)."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self._token_usage = {"input": 0, "output": 0}

    def chat(self, messages: list[dict], stream: bool = False, max_retries: int = 3) -> str:
        """Send chat completion request with retry logic."""
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens_per_request,
                    temperature=self.config.temperature,
                    stream=False,
                )
                choice = response.choices[0]
                self._token_usage["input"] += response.usage.prompt_tokens or 0
                self._token_usage["output"] += response.usage.completion_tokens or 0
                return choice.message.content or ""
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"LLM call failed after {max_retries} attempts: {last_error}")

    def chat_stream(self, messages: list[dict], on_token=None, max_retries: int = 3):
        """Send streaming chat completion. Yields content chunks."""
        last_error = None
        for attempt in range(max_retries):
            try:
                stream = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    max_tokens=self.config.max_tokens_per_request,
                    temperature=self.config.temperature,
                    stream=True,
                )
                full = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        full += delta.content
                        if on_token:
                            on_token(delta.content)
                return full
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"LLM stream failed after {max_retries} attempts: {last_error}")

    @property
    def token_usage(self) -> dict:
        return dict(self._token_usage)

    def reset_usage(self):
        self._token_usage = {"input": 0, "output": 0}
