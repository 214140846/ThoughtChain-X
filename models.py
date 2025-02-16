"""
模型调用模块，包含各种模型的调用逻辑
"""

import re
from typing import Generator, Optional
from api_client import APIClient
from config import DEFAULT_DEEPSEEK_SYSTEM_PROMPT, DEFAULT_CLAUDE_SYSTEM_PROMPT


class ModelManager:
    @staticmethod
    def call_deepseek(prompt: str) -> Generator[str, None, None]:
        """调用DeepSeek模型"""
        return APIClient.call_api(
            prompt=prompt,
            model="deepseek-reasoner",
            system_prompt=DEFAULT_DEEPSEEK_SYSTEM_PROMPT
        )

    @staticmethod
    def call_claude(
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

        return APIClient.call_api(
            prompt=full_prompt,
            model="claude-3-5-sonnet-20240620",
            system_prompt=system_prompt
        )

    @staticmethod
    def call_model(
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """通用模型调用接口"""
        return APIClient.call_api(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt
        )
