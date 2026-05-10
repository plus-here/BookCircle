# BookCircle 书圈网站启动说明

## 1. 项目信息

项目名称：BookCircle 书圈网站

论文题目：基于BS架构的书圈网站设计与实现

学生信息：22030206 杨嘉豪，计算机科学与技术

指导教师：赵东峰

## 2. 项目结构

```text
backend/          Django + Django REST Framework + Channels 后端
frontend-user/    Vue3 + Vite 用户端，默认端口 5173
frontend-admin/   Vue3 + Vite 管理端，默认端口 5174
Start-BookCircle.ps1       Windows 启动脚本
Stop-BookCircle.ps1        Windows 停止脚本
Start-BookCircle-Mac.sh    macOS/Linux 启动脚本
Stop-BookCircle-Mac.sh     macOS/Linux 停止脚本
.env.example               环境变量示例
README.md                  项目说明
```

## 3. 环境要求

推荐环境：

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Windows PowerShell，或 macOS/Linux Bash

说明：项目以 MySQL 作为主要数据库方案，同时支持 SQLite 本地演示配置。毕业答辩演示建议优先使用已导出的 MySQL 数据库。

## 4. Windows 启动方式

在项目根目录打开 PowerShell，执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-BookCircle.ps1 -HostName 0.0.0.0 -Https
```

启动成功后访问：

```text
用户端：https://localhost:5173/
管理端：https://localhost:5174/login
后端 API：http://127.0.0.1:8000/
WebSocket：ws://127.0.0.1:8001/
```

如果需要在手机上同 WiFi 访问，请使用启动脚本输出的局域网地址，例如：

```text
https://192.168.1.5:5173/
```

首次访问本地 HTTPS 地址时，手机或浏览器可能会出现证书提示，选择继续访问即可。视频通话需要允许摄像头和麦克风权限。

## 5. Windows 停止方式

在项目根目录执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\Stop-BookCircle.ps1
```

## 6. macOS/Linux 启动方式

进入项目根目录后执行：

```bash
chmod +x Start-BookCircle-Mac.sh Stop-BookCircle-Mac.sh
./Start-BookCircle-Mac.sh
```

如需让同 WiFi 手机访问，可以执行：

```bash
HOST_NAME=0.0.0.0 ./Start-BookCircle-Mac.sh
```

停止项目：

```bash
./Stop-BookCircle-Mac.sh
```

## 7. 数据库导入

如果使用 MySQL，请先创建数据库和用户，再导入随材料提供的 SQL 文件。

示例：

```sql
CREATE DATABASE bookcircle CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bookcircle_user'@'localhost' IDENTIFIED BY 'Bookcircle@123';
GRANT ALL PRIVILEGES ON bookcircle.* TO 'bookcircle_user'@'localhost';
FLUSH PRIVILEGES;
```

导入数据库：

```powershell
$env:MYSQL_PWD="Bookcircle@123"
mysql -u bookcircle_user -h 127.0.0.1 -P 3306 --default-character-set=utf8mb4 bookcircle < 22030206_杨嘉豪_BookCircle数据库.sql
```

如果只需要快速本地空库演示，也可以复制 `.env.example` 为 `.env`，并设置：

```text
BOOKCIRCLE_DB=sqlite
```

然后启动脚本会执行迁移，创建 SQLite 数据库。

## 8. 演示账号

管理员账号：

```text
admin / Admin@123456
```

普通用户账号：

```text
linan / BookCircle123!
zhouqian / BookCircle123!
```

其他种子用户密码一般也为：

```text
BookCircle123!
```

## 9. 功能演示建议

用户端建议演示：

- 登录和个人信息
- 首页图书浏览和搜索
- 图书详情和章节阅读
- 加入书架、记录阅读进度、章节书签
- 社团浏览、入社申请、帖子和评论
- 活动查看、报名和我的活动
- 公告查看
- 群聊、私聊和视频通话

管理端建议演示：

- 管理员登录
- 仪表盘统计
- 用户管理
- 图书管理
- 章节管理
- 社团管理和入社审批
- 活动管理
- 公告管理

## 10. 视频通话说明

视频通话通过 WebSocket 转发 WebRTC 信令实现。WebSocket 负责转发 offer、answer、ICE 等信令，音视频媒体流由 WebRTC 在浏览器之间建立连接。

当前项目适合本机多浏览器或同 WiFi 跨设备演示。如果需要跨公网稳定视频通话，需要配置正式 HTTPS 域名和 TURN 服务。

## 11. 常见问题

1. 页面能打开但聊天连接失败：确认 Daphne WebSocket 服务 8001 正常运行。
2. 手机无法登录：确认手机和电脑在同一 WiFi，并使用电脑局域网 IP 访问用户端。
3. 摄像头或麦克风不可用：确认浏览器访问方式为 HTTPS 或 localhost，并允许权限。
4. 管理端登录失败：确认使用管理员账号 `admin / Admin@123456`，并确认数据库已正确导入。
5. 数据库连接失败：检查 `.env` 中 MySQL 用户名、密码、数据库名和端口是否正确。
