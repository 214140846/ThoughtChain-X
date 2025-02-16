"""
API客户端模块，处理与API的通信
"""

import json
import http.client
from typing import Optional, Generator
from config import BASE_URL, API_KEY_SSVIP


class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def call_api(
        self,
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """调用API并返回响应"""
        # 验证必要参数
        if not self.base_url or not self.api_key:
            raise ValueError("API地址和密钥不能为空，请在设置中填写正确的API信息")

        if not prompt or not model:
            raise ValueError("提示词和模型名称不能为空")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
            "stream": True
        }

        if system_prompt:
            payload["messages"].insert(0, {
                "role": "system",
                "content": system_prompt
            })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }

        try:
            print(f"调用API: {self.base_url}/v1/chat/completions {self.api_key}")
            conn = http.client.HTTPSConnection(self.base_url)
            conn.request("POST", "/v1/chat/completions",
                         json.dumps(payload), headers)

            response = conn.getresponse()
            buffer = ""

            for chunk in response:
                if chunk:
                    try:
                        chunk_str = chunk.decode('utf-8')

                        if chunk_str.strip() == "":
                            continue

                        if chunk_str.startswith('data: '):
                            chunk_str = chunk_str.lstrip('data: ')

                        try:
                            data = json.loads(chunk_str)

                            if 'choices' in data and len(data['choices']) > 0:
                                if model.startswith('claude'):
                                    delta = data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        content = delta['content']
                                        buffer += content
                                        yield buffer
                                else:  # deepseek
                                    delta = data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        buffer += content
                                        yield buffer
                        except json.JSONDecodeError:
                            if chunk_str.strip():
                                buffer += chunk_str
                                yield buffer
                    except Exception as e:
                        print(f"解析响应出错: {str(e)}")
                        continue

            conn.close()
            return buffer

        except Exception as e:
            print(f"API 调用错误: {str(e)}")
            return None
