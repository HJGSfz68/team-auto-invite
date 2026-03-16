# ChatGPT Team Auto Invite

一个轻量级的 ChatGPT Team 席位自动邀请工具，兑换码机制分发 Team 席位，支持多母号轮询、后台管理面板和 Docker 一键部署。

## 功能

- **兑换码系统** — 支持批量生成/导入兑换码，可设置单码使用次数上限
- **多母号轮询** — 支持添加多个 Team 母号 JWT Token，满员后自动切换下一个
- **管理后台** — 密码登录，可管理兑换码、Token、查看邀请记录和统计数据
- **IP 频率限制** — 可配置的 IP 冷却时间，防止滥用

## 部署

### Docker Compose

```bash
git clone https://github.com/Futureppo/team-auto-invite
cd team-auto-invite
cp ".env example" .env
docker compose up -d
```

### Docker

```bash
git clone https://github.com/Futureppo/team-auto-invite
cd team-auto-invite
docker build -t team-auto-invite .
docker run -d -p 8080:8080 --env-file .env team-auto-invite
```

### 本地运行

```bash
pip install -r requirements.txt
python app.py
```

## 环境变量

| 变量                 | 说明                 | 默认值                     |
| -------------------- | -------------------- | -------------------------- |
| `ADMIN_PASSWORD`     | 后台管理密码         | 空（未设置则无法登录后台） |
| `PORT`               | 服务端口             | `8080`                     |
| `SECRET_KEY`         | Flask Session 密钥   | 自动生成                   |
| `OAI_CLIENT_VERSION` | ChatGPT 客户端版本号 | 内置默认值                 |


## License

AGPLv3
