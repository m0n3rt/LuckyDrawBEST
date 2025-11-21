"""一键运行脚本（Python 版本）
功能:
1. 检查/创建虚拟环境 .venv (使用当前解释器)
2. 安装后端依赖 (backend/requirements.txt)
3. 启动 uvicorn 后端 (后台子进程)
4. 自动打开浏览器访问 /ui 界面

用法:
python run_all.py                # 默认端口 8000
python run_all.py --port 9000    # 指定端口
python run_all.py --no-browser   # 不自动打开浏览器
python run_all.py --no-backend   # 仅打开浏览器（假设后端已启动）

注意: Windows 上运行，若之前已使用 start.ps1 可选择其之一。
"""

import os, sys, subprocess, time, webbrowser, threading, shutil
from pathlib import Path

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="LuckyDraw 一键运行")
    p.add_argument('--port', type=int, default=8000, help='后端端口')
    p.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    p.add_argument('--no-backend', action='store_true', help='跳过后端启动')
    return p.parse_args()

ROOT = Path(__file__).parent.resolve()
VENV = ROOT/'.venv'
PY_BIN = VENV/'Scripts'/'python.exe' if os.name == 'nt' else VENV/'bin'/'python'
REQ = ROOT/'backend'/'requirements.txt'

def log(msg):
    print(f"[run_all] {msg}")

def ensure_venv():
    if PY_BIN.exists():
        log("虚拟环境已存在，跳过创建")
        return
    log(f"创建虚拟环境: {PY_BIN}")
    subprocess.check_call([sys.executable, '-m', 'venv', str(VENV)])

def install_deps():
    if not REQ.exists():
        log(f"未找到依赖文件: {REQ}")
        return
    marker = VENV/'.deps_installed'
    if marker.exists():
        log("发现依赖安装标记，跳过安装。如需重新安装删除 .deps_installed")
        return
    log("开始安装依赖 ...")
    subprocess.check_call([str(PY_BIN), '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([str(PY_BIN), '-m', 'pip', 'install', '-r', str(REQ)])
    marker.write_text("ok")
    log("依赖安装完成")

def start_backend(port: int):
    log(f"启动后端 uvicorn (端口 {port})")
    # 使用新的子进程启动 uvicorn
    # 注意: 如需查看日志可不使用 creationflags
    cmd = [str(PY_BIN), '-m', 'uvicorn', 'backend.app.main:app', '--host', '127.0.0.1', '--port', str(port), '--reload']
    # 打开独立窗口（仅 Windows）
    creationflags = 0x00000010 if os.name == 'nt' else 0  # CREATE_NEW_CONSOLE
    proc = subprocess.Popen(cmd, cwd=str(ROOT), creationflags=creationflags)
    return proc

def wait_server(port: int, timeout: float = 10.0):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(0.5)
                s.connect(('127.0.0.1', port))
                return True
            except Exception:
                time.sleep(0.4)
    return False

def open_browser(port: int):
    url = f"http://127.0.0.1:{port}/ui"
    log(f"打开浏览器: {url}")
    webbrowser.open(url)

def main():
    args = parse_args()
    log(f"使用解释器: {sys.executable}")
    ensure_venv()
    install_deps()
    backend_proc = None
    if not args.no_backend:
        backend_proc = start_backend(args.port)
        log("等待后端启动...")
        if wait_server(args.port):
            log("后端启动成功")
        else:
            log("后端在限定时间内未响应，可检查独立窗口日志")
    else:
        log("跳过后端启动 (假设已在其他终端运行)")
    if not args.no_browser:
        open_browser(args.port)
    else:
        log("已选择不自动打开浏览器")
    log("脚本完成，后端在独立窗口中运行 (若已启动)。")

if __name__ == '__main__':
    main()