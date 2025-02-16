"""
模型调用模块，包含各种模型的调用逻辑
"""

import re
from typing import Generator, Optional
from api_client import APIClient
from config import DEFAULT_DEEPSEEK_SYSTEM_PROMPT, DEFAULT_CLAUDE_SYSTEM_PROMPT


class ModelManager:
    def __init__(self, base_url=None, api_key=None):
        self.api_client = APIClient(base_url, api_key)

    def update_api_settings(self, url: str, key: str):
        """更新API设置"""
        self.api_client.base_url = url
        self.api_client.api_key = key

    def call_deepseek(self, prompt: str) -> Generator[str, None, None]:
        """调用DeepSeek模型"""
        return self.api_client.call_api(
            prompt=prompt,
            model="deepseek-reasoner",
            system_prompt=DEFAULT_DEEPSEEK_SYSTEM_PROMPT
        )

    def call_claude(
        self,
        prompt: str,
        deepseek_result: str = ""
    ) -> Generator[str, None, None]:
        """调用Claude模型"""
        if deepseek_result:
            # 从deepseek_result中提取<think></think>标签内的内容作为Claude的系统提示
            think_content = re.search(
                r'<think>(.*?)</think>', deepseek_result, re.DOTALL)
            system_prompt = (think_content.group(1).strip() +
                             f"\n\n用户原始输入: {prompt}") if think_content else ""

            full_prompt = prompt
        else:
            system_prompt = DEFAULT_CLAUDE_SYSTEM_PROMPT
            full_prompt = prompt

        return self.api_client.call_api(
            prompt=full_prompt,
            model="claude-3-5-sonnet-20240620",
            system_prompt=system_prompt
        )

    def call_model(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """通用模型调用接口"""
        return self.api_client.call_api(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt
        )
