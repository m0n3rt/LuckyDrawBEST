**项目概览**
- **名称**: LuckyDrawBEST — 桌面抽奖客户端 + 后端原型
- **用途**: 提供一个美化过的桌面抽奖界面（Tkinter），以及一个用于扫码/注册与权威抽奖的 FastAPI 后端原型。

**先决条件**
- **操作系统**: Windows（已在该环境下开发并测试）
- **Python**: 推荐 Python 3.10+（本仓库在多机/多解释器下测试通过，示例使用 Python 3.12 和另一个 D:/PYTHON 解释器）。
- **网络**: 本地运行时需要允许 `127.0.0.1:8000` 通信。

**目录结构（关键）**
- `LuckyDrawBEST.py`：桌面客户端主程序（Tkinter）。
- `爽抽.py`：原始/备用客户端脚本（保留历史）。
- `backend/`：后端原型目录（FastAPI + SQLAlchemy）。
  - `backend/app/main.py`：FastAPI entrypoint。
  - `backend/app/routers`：API 路由（participants、draw、websocket）。
  - `backend/requirements.txt`：后端依赖清单。

**快速运行（推荐虚拟环境）**
1) 打开 PowerShell，进入项目根目录：

```powershell
Set-Location "D:\桌面大文件夹\VScode\LuckyDrawBEST"
```

2) 使用系统 Python（示例使用已配置的 Python312）创建并激活虚拟环境：

```powershell
C:/Users/25703/AppData/Local/Programs/Python/Python312/python.exe -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

3) 安装后端依赖：

```powershell
pip install -r backend/requirements.txt
```

4) 启动后端服务：

```powershell
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

5) 在浏览器打开 API 文档： `http://127.0.0.1:8000/docs`，可通过 Swagger 快速注册参与者并测试 `/api/draw`。

6) 启动桌面客户端（同一虚拟环境或使用任意已安装依赖的解释器）：

```powershell
python LuckyDrawBEST.py
# 或者指定解释器运行
C:/Users/25703/AppData/Local/Programs/Python/Python312/python.exe LuckyDrawBEST.py
```

**客户端使用指南**
- **后端模式开关**: 在控制面板打开“后端模式”（开关为绿色为开启）。开启后客户端在最终确认中奖时会调用后端 `/api/draw` 获取权威结果。
- **后端 URL**: 默认 `http://127.0.0.1:8000`，可在控制面板中修改并保存（无持久化，仅会话内有效）。
- **刷新参与者**: 点击“刷新参与者”将调用 `/api/participants` 并显示参与者总数（用于确认后端注册是否可用）。
- **抽奖流程**: 与原本本地动画一致（每次抽奖保留视觉效果）；当后端模式开启且后端返回有效结果时，最终中奖号码会被后端结果覆盖（客户端会提示并保存公平性信息）。
- **公平性面板**: 抽取成功后可展开“公平性(展开/折叠)”面板查看 `Seed` / `PrevChain` / `HashChain`，并支持一键复制。

**后端接口（快速概览）**
- `POST /api/register` : 注册参与者并发放票号。
- `GET /api/participants` : 列表查询参与者（支持 `skip`/`limit`）。
- `POST /api/draw` : 后端进行一次抽奖（请求包含 `prize_level` 与 `count`），返回 `session`, `winners` 与 `prev_chain`。

**公平性说明**
- 抽奖使用链式哈希机制：后端为每次抽奖生成 `seed`（基于时间戳、当前票数与 salt），并用 `seed + prev_hash` 生成新的 `hash_chain`，把 `seed` 和 `hash_chain` 存入 `DrawSession`。返回给客户端 `prev_chain` 用于链条校验与审计。
- 若需要验证，导出 `Seed`、`PrevChain`、`HashChain` 并在可信脚本中重放随机数生成顺序以复现结果。

**常见问题与排查**
- 报 ImportError（例如 pydantic/fastapi 找不到）: 检查你运行客户端/后端使用的 Python 解释器是否与安装依赖时一致；在 VS Code 中请把解释器切换为你用于安装依赖的那个，或在目标解释器上重新运行 `pip install -r backend/requirements.txt`。
- 后端无法启动（端口被占用）: 修改 `--port` 参数或结束占用进程。
- 刷新参与者失败: 确认后端已启动且 `backend URL` 填写正确（不要包含尾部斜杠或空格），同时查看后端终端日志。
- 抽奖后号码仍为本地：确认“后端模式”开关为开启，检查后端 `/api/draw` 返回是否成功。

**一键启动脚本**
- 提供 `start.ps1`：自动创建 `.venv`、安装依赖并启动后端与客户端。
- 用法示例（当前目录下）：
  ```powershell
  powershell -ExecutionPolicy Bypass -File .\start.ps1
  # 只启动后端：
  powershell -ExecutionPolicy Bypass -File .\start.ps1 -NoClient
  # 只启动客户端：
  powershell -ExecutionPolicy Bypass -File .\start.ps1 -NoBackend
  # 自定义端口：
  powershell -ExecutionPolicy Bypass -File .\start.ps1 -Port 9000
  ```
- 双击运行：使用 `start.bat`（内部调用 PowerShell）。
- 若执行策略受限，可先： `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`。

**网页前端 /ui**
- 新增简易 Web UI 路由：启动后端后访问 `http://127.0.0.1:8000/ui`。
- 功能：注册参与者、刷新列表、执行抽奖、查看公平性 Seed / PrevChain / HashChain 并复制。
- 适用场景：无需桌面 Tkinter 客户端时，用浏览器即可演示。
- 注意：浏览器抽奖调用的是后端权威逻辑；若需要本地动画体验仍使用 `LuckyDrawBEST.py`。

**分步运行（Python 3.12）**
1. 选择解释器: 确保 VS Code 右下角选择 `Python312` (路径: `C:/Users/25703/.../Python312/python.exe`).
2. 创建虚拟环境:
  ```powershell
  C:/Users/25703/AppData/Local/Programs/Python/Python312/python.exe -m venv .venv
  . .\.venv\Scripts\Activate.ps1
  ```
3. 安装依赖:
  ```powershell
  pip install -r backend/requirements.txt
  ```
4. 启动后端:
  ```powershell
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
  ```
5. 浏览器访问: `http://127.0.0.1:8000/ui` （或 API 文档 `http://127.0.0.1:8000/docs`）
6. 启动桌面客户端(另一个终端):
  ```powershell
  python LuckyDrawBEST.py
  ```

**一键运行 (Python 脚本版)**
- 使用 `run_all.py` 自动完成虚拟环境创建/依赖安装/后端启动/打开网页:
  ```powershell
  python run_all.py              # 默认端口 8000
  python run_all.py --port 9001  # 自定义端口
  python run_all.py --no-browser # 不自动打开浏览器
  python run_all.py --no-backend # 仅打开浏览器 (假设后端已在别处启动)
  ```
- 若再次运行且依赖已安装，会跳过重复安装；删除 `.venv/.deps_installed` 可强制重新安装。

**遇到后端立即退出的排查**
- 若出现启动后立刻 `Shutting down`: 可能是被外部脚本/终端关闭；确保在独立终端前台运行。
- 尝试加调试日志:
  ```powershell
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --log-level debug
  ```
- 检查是否端口冲突（改用 `--port 8001`）或安全软件拦截。


**开发者提示**
- 若要在不同机器上做展示，可把后端部署到可访问的主机并在客户端输入对应地址（注意 CORS 和防火墙）。
- 想进一步扩展：实现 WebSocket 广播实时更新参与者、增加管理员鉴权、短信/邮箱通知推送适配器。

**致谢与联系方式**
- 这是一个演示/原型工程；如需我帮你把它打包为可执行文件（PyInstaller）或继续开发新功能（WebSocket、通知集成、管理后台），告诉我你的优先项。

---
（如需我拆分为更细的 `backend/README.md` 或 `client/README.md`，我可以继续。）
 
**发布到 GitHub**
- 初始化仓库（若尚未执行）：
  ```powershell
  git init
  git add .
  git commit -m "chore: initial commit"
  git branch -M main
  git remote add origin <你的仓库URL>
  git push -u origin main
  ```
- 后续提交示例：
  ```powershell
  git add backend/app/routers/frontend.py
  git commit -m "feat: add animated draw screen"
  git push
  ```
- 常见发布注意：确保 `.gitignore` 已包含 `.venv/`、`__pycache__/`、本地数据库 `luckydraw.db` 等；不要提交 `.env` 或私密令牌。

**扫码登记（二维码方案）**
- 目标：让现场用户通过手机扫码访问 `http://<你的主机或局域网IP>:8000/register_form` 并填写登记表单。
- 步骤：
  1. 确保后端已在可访问的地址启动（若是局域网，使用本机局域网 IP 替换 127.0.0.1）。
  2. 安装二维码库：`pip install qrcode[pil]`。
  3. 使用示例脚本生成二维码 PNG（见下方 `qr_example.py`）。
  4. 将生成的 `register_qr.png` 投影或打印出来，现场扫码即可访问登记页。
- 安全提示：如在公共网络上使用，请考虑在后端加入简单的访问令牌或限流逻辑，避免恶意刷票。

**二维码示例脚本 (`qr_example.py`)**
```python
import qrcode

def gen_register_qr(base_url: str = "http://127.0.0.1:8000"):
    target = base_url.rstrip('/') + '/register_form'
    img = qrcode.make(target)
    img.save('register_qr.png')
    print('生成二维码 -> register_qr.png 指向:', target)

if __name__ == '__main__':
    # 将 base_url 换成你的局域网 IP 或已部署域名
    gen_register_qr("http://192.168.1.88:8000")
```

**部署与公网访问简述**
- 简单局域网：同一 Wi-Fi 下其他设备可直接访问 `http://<你的局域网IP>:8000/ui`。
- 生产 / 公网：可选用 `uvicorn` + `--host 0.0.0.0` 暴露，或通过 Nginx 反向代理。建议使用：
  ```powershell
  uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2
  ```
- 若需要 HTTPS：在前置 Nginx/Traefik/Caddy 上配置 TLS，将流量转发到内部 8000 端口。

**后续可拓展清单（Ideas）**
- 增加管理员面板（查看统计、手动撤销中奖记录）。
- 更丰富的公平性验证脚本（生成可复现的随机序列文件）。
- WebSocket 加入心跳与断线重连策略。
- 支持手机号或邮箱验证，防止重复注册。
- 增加奖品层级与批次管理（session 分组）。

**贡献**
- 欢迎提交 Issue/PR：说明你的改动意图与测试方式。
- 建议的 Commit 格式：`feat:` / `fix:` / `chore:` / `docs:` / `refactor:` / `test:` 前缀。

**License**
- 当前未附加 License，作为内部/学习用途；若需公开开源可考虑添加 MIT 或 Apache-2.0 许可证文件。
