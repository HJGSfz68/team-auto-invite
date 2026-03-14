# ChatGPT Team Auto Invite

一个轻量级的 ChatGPT Team 席位自动邀请工具。通过 Web 页面输入邮箱即可自动发送 Team 邀请，支持 Docker 一键部署。

## 功能

- 通过 Web 界面输入邮箱，一键发送 ChatGPT Team 席位邀请
- 自动解析 JWT Token，提取账户信息并校验有效性
- 使用 curl_cffi 模拟 Chrome 浏览器指纹，绕过 Cloudflare 检测
- 支持 Token 过期检测与计划类型校验
- 提供健康检查接口，便于监控服务状态
- 支持 Docker / Docker Compose 部署

## 项目结构

```
team-auto-invite/
├── app.py                 # Flask 后端主程序
├── static/
│   └── index.html         # 前端页面
├── Dockerfile             # Docker 镜像构建
├── docker-compose.yml     # Docker Compose 编排
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置（不纳入版本控制）
├── .gitignore
└── .dockerignore
```

## 环境变量

| 变量名 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `JWT_TOKEN` | 是 | - | ChatGPT Team 管理员账户的 JWT Token |
| `OAI_CLIENT_VERSION` | 否 | `prod-eddc2f6ff65fee2d0d6439e379eab94fe3047f72` | ChatGPT 客户端版本号 |
| `PORT` | 否 | `8080` | 服务监听端口 |

## 部署

### Docker Compose（推荐）

1. 编辑 `.env` 文件，填入 JWT Token：

```env
JWT_TOKEN=eyJhbGciOi...
```

2. 启动服务：

```bash
docker compose up -d
```

3. 访问 `http://localhost:8080` 即可使用。

### Docker

```bash
docker build -t team-auto-invite .
docker run -d -p 8080:8080 --env-file .env team-auto-invite
```

### 本地运行

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置 `.env` 文件后运行：

```bash
python app.py
```

## API

### POST /api/invite

发送 Team 邀请。

请求体：

```json
{
  "email": "user@example.com"
}
```

响应示例：

```json
{
  "success": true,
  "message": "邀请发送成功，请检查邮箱"
}
```

### GET /api/health

健康检查接口，返回服务状态和 Token 有效性。

响应示例：

```json
{
  "status": "ok",
  "token_valid": true,
  "message": "服务正常"
}
```

## 技术栈

- **后端**: Python / Flask / Gunicorn
- **HTTP 客户端**: curl_cffi（浏览器指纹模拟）
- **前端**: 原生 HTML / CSS / JavaScript
- **部署**: Docker / Docker Compose

## 获取 JWT Token

1. 登录 [chatgpt.com](https://chatgpt.com)
2. 打开浏览器开发者工具（F12）
3. 在 Network 面板中找到任意 API 请求
4. 从请求头中复制 `Authorization: Bearer` 后面的 Token
5. 将 Token 填入 `.env` 文件的 `JWT_TOKEN` 字段

## License

MIT
