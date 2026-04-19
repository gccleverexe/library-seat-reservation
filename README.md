# 校园图书馆座位预约系统

基于 FastAPI + 原生 HTML/JS 的轻量级图书馆座位预约平台，支持学生在线预约、签到签退，以及管理员后台管理。

---

## 功能特性

**学生端**
- 注册 / 登录（JWT 鉴权，连续错误自动锁定）
- 按楼层、区域、时段筛选可用座位
- 创建 / 取消预约（单次最长 4 小时）
- 签到（开始前 10 分钟至开始后 15 分钟内有效）/ 签退
- 查看历史预约记录

**自动化**
- 超时未签到自动释放座位并记录违规
- 累计 3 次违规自动限制预约权限 7 天

**管理员端**
- 座位增删改查 / 状态管理
- 预约记录查询与强制取消
- 违规记录查询与手动解除限制
- 数据统计看板（预约完成率、热门座位、分时段分布、违规统计）

---

## 快速启动

> 需要 Python 3.10+

**Windows 一键启动：**

```bat
start.bat
```

启动后自动打开浏览器，服务地址：

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

默认管理员账号：`admin` / `admin123`

**手动启动：**

```bash
pip install -r requirements.txt

# 后端
python -m uvicorn backend.main:app --reload --port 8000

# 前端（新终端）
cd frontend && python -m http.server 3000
```

---

## 项目结构

```
library-seat-reservation/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（JWT 密钥、超时参数等）
│   ├── database.py          # SQLAlchemy 数据库连接
│   ├── dependencies.py      # 依赖注入（当前用户、管理员校验）
│   ├── init_db.py           # 数据库初始化 & 种子数据
│   ├── models/              # ORM 模型（User / Seat / Reservation / Violation）
│   ├── schemas/             # Pydantic 请求/响应模型
│   ├── routers/             # 路由（auth / seats / reservations / checkin / admin）
│   └── services/            # 业务逻辑（预约、签到、调度器、看板等）
├── frontend/
│   ├── index.html           # 入口（重定向到登录页）
│   ├── pages/               # login / seats / reservation / admin
│   └── js/                  # api.js / auth.js / seats.js / admin.js
├── requirements.txt
├── start.bat                # Windows 一键启动脚本
└── library.db               # SQLite 数据库（首次启动自动生成）
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python · FastAPI · SQLAlchemy · APScheduler |
| 认证 | JWT (python-jose) · bcrypt (passlib) |
| 数据库 | SQLite |
| 前端 | 原生 HTML / CSS / JavaScript |
