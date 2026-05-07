# BookCircle 书圈

BookCircle 是一个读书社区项目，包含用户端、管理端、Django API 和 WebSocket 服务。当前适合本地演示、同 WiFi 多设备测试，以及继续扩展为正式部署版本。

## 功能概览

- 账号：注册、登录、JWT 自动刷新、个人资料、头像、退出登录。
- 图书阅读：图书列表、搜索、详情、章节阅读、书架、阅读进度、章节书签。
- 社团：社团列表、社团详情、申请加入、成员展示、板块、帖子、评论、申请审批。
- 群组：创建/加入/退出群组，WebSocket 群聊。
- 私聊：一对一会话、实时消息、跨浏览器/同 WiFi 视频通话。
- 活动：活动列表、详情、报名、取消报名、报名人数、可选名额和剩余席位。
- 公告：公告列表和详情。
- 管理端：图书、章节、社团、活动、公告等基础管理。

## 项目结构

```text
backend/          Django + DRF + Channels
frontend-user/    Vue 用户端，默认端口 5173
frontend-admin/   Vue 管理端，默认端口 5174
Start-BookCircle.ps1       Windows 启动脚本
Stop-BookCircle.ps1        Windows 停止脚本
Start-BookCircle-Mac.sh    macOS/Linux 启动脚本
Stop-BookCircle-Mac.sh     macOS/Linux 停止脚本
```

## 推荐迁移方式

推荐推送到 GitHub，再在 Mac 上 `git clone`。这样最省心：

- 代码改动有版本记录，之后 Windows 和 Mac 可以互相同步。
- 不会把 `node_modules`、虚拟环境、日志、证书、SQLite 数据库这类机器相关文件带过去。
- 后续部署到服务器或回滚都更稳。

直接打包发过去也能跑，但请只打包源码，不要带 `frontend-*/node_modules`、`backend/.venv*`、日志和 `.cert`。

## macOS 本地启动

### 1. 安装基础环境

建议先装 Homebrew，然后安装 Python 和 Node：

```bash
brew install python node
```

如果要用 MySQL 保留原有数据，再安装 MySQL 客户端依赖：

```bash
brew install pkg-config mysql-client
```

如果只想快速在 Mac 上跑一个空库演示，用 SQLite 即可，不需要启动 MySQL。

### 2. 获取项目

推荐：

```bash
git clone <你的 GitHub 仓库地址>
cd codex
```

如果是压缩包，就解压后进入项目根目录。

### 3. 准备环境变量

快速演示用 SQLite：

```bash
cp .env.example .env
```

确认 `.env` 里是：

```bash
BOOKCIRCLE_DB=sqlite
```

如果要连接 MySQL，把 `.env` 改为：

```bash
BOOKCIRCLE_DB=mysql
MYSQL_DATABASE=bookcircle
MYSQL_USER=bookcircle_user
MYSQL_PASSWORD=你的本地数据库密码
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
```

### 4. 启动

```bash
chmod +x Start-BookCircle-Mac.sh Stop-BookCircle-Mac.sh
./Start-BookCircle-Mac.sh
```

启动后打开：

- 用户端：`http://localhost:5173/`
- 管理端：`http://localhost:5174/login`
- API：`http://localhost:8000/`
- WebSocket：`ws://localhost:8001/`

停止：

```bash
./Stop-BookCircle-Mac.sh
```

## Windows 本地启动

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-BookCircle.ps1 -HostName 0.0.0.0 -Https
```

停止：

```powershell
powershell -ExecutionPolicy Bypass -File .\Stop-BookCircle.ps1
```

## 手动启动方式

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

WebSocket：

```bash
cd backend
source .venv/bin/activate
daphne -b 127.0.0.1 -p 8001 config.asgi:application
```

用户端：

```bash
cd frontend-user
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

管理端：

```bash
cd frontend-admin
npm install
npm run dev -- --host 127.0.0.1 --port 5174
```

## 账号和数据

Mac 上如果使用 SQLite，会是一个新的空数据库。先创建管理员：

```bash
cd backend
source .venv/bin/activate
python manage.py createsuperuser
```

如果要把 Windows 上的演示数据带到 Mac，建议在 Windows 导出数据库，再在 Mac 导入 MySQL。SQLite 适合快速演示空项目，MySQL 更适合保留原有数据。

## 视频通话说明

同 WiFi 演示可用本地 HTTPS 或 localhost。跨公网稳定通话需要：

- 正式 HTTPS 域名。
- TURN 服务。
- 在 `frontend-user` 环境变量中配置 `VITE_RTC_ICE_SERVERS`。

示例：

```bash
VITE_RTC_ICE_SERVERS='[{"urls":"turn:your-domain:3478","username":"user","credential":"pass"}]'
```

## 常见问题

- `mysqlclient` 安装失败：Mac 上先安装 `mysql-client` 和 `pkg-config`，并确保 shell 能找到 MySQL client。
- 手机不能访问电脑：启动时把 `HOST_NAME=0.0.0.0` 放到命令前，例如 `HOST_NAME=0.0.0.0 ./Start-BookCircle-Mac.sh`，并确认防火墙允许访问。
- 页面能打开但聊天断开：确认 8001 Daphne 服务正在运行，且前端通过同源 `/ws` 代理或正确的 WebSocket 地址连接。
