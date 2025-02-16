"""
主程序入口
"""

import threading
from utils import watch_file_changes
from ui import launch_ui


def main():
    # 启动文件监控线程
    monitor_thread = threading.Thread(target=watch_file_changes)
    monitor_thread.daemon = True
    monitor_thread.start()
    # 启动UI
    launch_ui()


if __name__ == "__main__":
    main()
