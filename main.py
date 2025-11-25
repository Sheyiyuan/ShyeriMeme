from api.api import shyeri_meme_app
import uvicorn
import socket
import requests
import time
from core.core import conf
from utils.log import setup_global_redirect

PORT = conf.get()["api"]["port"]

def is_port_occupied(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def is_self_process_running(port):
    """检查占用端口的是否是本项目进程"""
    try:
        # 等待一下，确保服务已经启动
        time.sleep(0.5)
        response = requests.get(f"http://localhost:{port}/list", timeout=2)
        # 检查响应是否符合本项目的格式
        if response.status_code == 200:
            data = response.json()
            # 检查是否包含本项目特有的字段结构
            if isinstance(data, dict) and 'data' in data and 'background_list' in data['data']:
                return True
    except (requests.RequestException, ValueError, KeyError):
        pass
    return False


# 在应用启动时设置全局输出重定向
try:
    original_stdout, original_stderr = setup_global_redirect()
    print("全局日志重定向已设置")
except Exception as e:
    print(f"设置日志重定向失败: {e}")

if __name__ == '__main__':
    print(f"尝试启动服务在端口 {PORT}")
    
    # 检查端口是否被占用
    if is_port_occupied(PORT):
        print(f"端口 {PORT} 已被占用，正在检查是否是本项目进程...")
        
        # 检查是否是本项目进程
        if is_self_process_running(PORT):
            print("✓ 当前项目已经在运行中！")
            print(f"请访问 http://localhost:{PORT} 查看应用")
            exit(0)  # 正常退出，因为应用已经在运行
        else:
            print(f"✗ 端口 {PORT} 被其他进程占用！")
            print("请关闭占用该端口的进程，或修改配置文件中的端口号。")
            exit(1)  # 异常退出，因为端口被其他进程占用
    
    # 端口可用，启动服务
    print(f"服务启动中... 端口: {PORT}")
    try:
        uvicorn.run(shyeri_meme_app, host='0.0.0.0', port=PORT)
    except Exception as e:
        print(f"启动服务时发生错误: {e}")
        exit(1)