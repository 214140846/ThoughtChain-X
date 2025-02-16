"""
API客户端模块，处理与API的通信
"""

import json
import http.client
from typing import Optional, Generator
from config import BASE_URL, API_KEY_SSVIP


class APIClient:
    @staticmethod
    def call_api(
        prompt: str,
        model: str,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """调用API并返回响应"""

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
            'Authorization': f'Bearer {API_KEY_SSVIP}',
            'Accept': 'application/json'
        }

        try:
            conn = http.client.HTTPSConnection(BASE_URL)
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
