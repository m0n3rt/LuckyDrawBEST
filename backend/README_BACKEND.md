# LuckyDraw 后端原型

## 功能概述
- 注册参与者并自动分配抽奖号码(递增)
- 列出参与者 (分页)
- 发起抽奖记录随机种子与哈希链 (公平可验证雏形)
- WebSocket 占位用于后续实时推送注册/中奖事件

## 技术栈
- FastAPI + SQLAlchemy + Pydantic
- SQLite (原型) 可升级 PostgreSQL

## 安装依赖
```bash
pip install -r backend/requirements.txt
```

## 启动服务
```bash
uvicorn backend.app.main:app --reload
```
访问: http://127.0.0.1:8000/docs 查看交互式接口文档。

## 主要接口
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/register | 注册参与者并返回号码 |
| GET  | /api/participants | 查询参与者列表 |
| POST | /api/draw | 发起抽奖，返回 winners |
| GET  | /health | 健康检查 |
| WS   | /ws/live | WebSocket 占位 |

## 抽奖公平性说明
- 种子生成: `time + ticket_count + previous_hash + salt` 取 SHA256 前16位
- 哈希链: `sha256(seed + previous_hash)` 形成可追溯链
- 使用 `random.Random(seed)` 洗牌票池，取前 count 个即为获奖结果。

## 后续待办
- 中奖事件 WebSocket 广播
- 管理后台与认证
- 短信/邮件通知
- 权重与分组模式
- 审计与风控

## 注意
桌面抽奖逻辑暂不改动，将在后续通过调用 /api/draw 接口对接。
