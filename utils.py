"""
工具函数模块，包含各种辅助功能
"""

import os
import sys
import time
from pathlib import Path


def watch_file_changes():
    """监控文件变化并自动重载"""
    current_file = Path(__file__)
    last_modified = current_file.stat().st_mtime

    while True:
        time.sleep(1)
        try:
            current_modified = current_file.stat().st_mtime
            if current_modified > last_modified:
                print("检测到文件变化，正在重启服务...")
                os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            print(f"监控文件变化时出错: {e}")


def format_response(response: str) -> str:
    """格式化响应文本"""
    return response.strip()
