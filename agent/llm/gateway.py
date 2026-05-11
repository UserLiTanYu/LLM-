"""LLM 网关模块 — 统一封装 DeepSeek API 调用。

使用 OpenAI 兼容的 SDK 与 DeepSeek API 通信。
提供两种调用模式：
  chat():        同步请求，返回完整响应（用于设计、实现、测试节点）
  chat_stream(): 流式请求，逐 token 回调（预留用于实时输出场景）

内置指数退避重试机制（最多 3 次），并提供 token 用量统计。
"""

import time
from openai import OpenAI
from agent.config import AgentConfig


class LLMGateway:
    """统一的 LLM 调用接口，封装 DeepSeek API（OpenAI 兼容协议）。"""

    def __init__(self, config: AgentConfig):
        """初始化 OpenAI 客户端，设置 token 统计计数器。"""
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self._token_usage = {"input": 0, "output": 0}

    def chat(self, messages: list[dict], stream: bool = False, max_retries: int = 3) -> str:
        """发送同步聊天请求，带指数退避重试。

        参数:
          messages:    OpenAI 格式的消息列表 [{"role":..., "content":...}]
          stream:      预留参数（当前仅同步模式）
          max_retries: 最大重试次数

        返回:
          LLM 回复的文本内容

        异常:
          RuntimeError: 所有重试均失败时抛出
        """
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
                # 累计 token 消耗（输入 + 输出）
                self._token_usage["input"] += response.usage.prompt_tokens or 0
                self._token_usage["output"] += response.usage.completion_tokens or 0
                return choice.message.content or ""
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # 指数退避：1s, 2s, 4s...
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"LLM 调用失败（已重试 {max_retries} 次）: {last_error}")

    def chat_stream(self, messages: list[dict], on_token=None, max_retries: int = 3):
        """发送流式聊天请求，实时回调每个 token。

        参数:
          messages:    OpenAI 格式的消息列表
          on_token:    可选回调函数，每收到一个 token 时调用 on_token(token_text)
          max_retries: 最大重试次数

        返回:
          完整的响应文本

        异常:
          RuntimeError: 所有重试均失败时抛出
        """
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
        raise RuntimeError(f"LLM 流式调用失败（已重试 {max_retries} 次）: {last_error}")

    @property
    def token_usage(self) -> dict:
        """返回当前累计的 token 用量 {input, output}。"""
        return dict(self._token_usage)

    def reset_usage(self):
        """重置 token 计数器。"""
        self._token_usage = {"input": 0, "output": 0}
