"""ChatGPT Team 自动邀请"""

import os
import jwt
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from curl_cffi import requests as cffi_requests
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")

JWT_TOKEN = os.getenv("JWT_TOKEN", "")
OAI_CLIENT_VERSION = os.getenv(
    "OAI_CLIENT_VERSION", "prod-eddc2f6ff65fee2d0d6439e379eab94fe3047f72"
)
PORT = int(os.getenv("PORT", "8080"))
BASE_URL = "https://chatgpt.com/backend-api"
_token_cache = None


def decode_token(token: str) -> dict:
    """解码 JWT，提取 account_id 等信息"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        auth = decoded.get("https://api.openai.com/auth", {})
        profile = decoded.get("https://api.openai.com/profile", {})
        return {
            "account_id": auth.get("chatgpt_account_id", ""),
            "plan_type": auth.get("chatgpt_plan_type", ""),
            "email": profile.get("email", ""),
            "exp": decoded.get("exp", 0),
            "valid": True,
        }
    except Exception as e:
        logger.error(f"JWT 解码失败: {e}")
        return {"valid": False, "error": str(e)}


def check_token_status() -> dict:
    """检查 Token 状态"""
    global _token_cache
    if not JWT_TOKEN:
        return {"ok": False, "error": "未配置 JWT_TOKEN，请在 .env 文件中设置"}

    if _token_cache is None:
        _token_cache = decode_token(JWT_TOKEN)

    info = _token_cache
    if not info["valid"]:
        return {"ok": False, "error": f"Token 解码失败: {info.get('error', '未知错误')}"}

    if info["exp"] < int(datetime.now(timezone.utc).timestamp()):
        return {"ok": False, "error": "Token 已过期，请更新 .env 中的 JWT_TOKEN"}
    if info["plan_type"] != "team":
        return {"ok": False, "error": f"当前 Token 不是 Team 类型（当前: {info['plan_type']}）"}

    return {"ok": True, "account_id": info["account_id"], "email": info["email"]}


def send_invite(account_id: str, email: str) -> dict:
    """发送 Team 邀请"""
    url = f"{BASE_URL}/accounts/{account_id}/invites"
    headers = {
        "Accept": "*/*",
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json",
        "OAI-Client-Version": OAI_CLIENT_VERSION,
        "OAI-Language": "zh-CN",
        "Origin": "https://chatgpt.com",
        "Referer": "https://chatgpt.com/admin/members",
        "chatgpt-account-id": account_id,
    }
    payload = {"email_addresses": [email], "role": "standard-user", "resend_emails": True}

    try:
        resp = cffi_requests.post(url, json=payload, headers=headers, impersonate="chrome", timeout=30)
        status = resp.status_code

        if status == 200:
            logger.info(f"邀请发送成功: {email}")
            return {"success": True, "message": "邀请发送成功，请检查邮箱"}
        if status == 409:
            logger.warning(f"邀请冲突: {email} (已邀请或已是成员)")
            return {"success": False, "message": "该邮箱已被邀请或已是团队成员"}
        if status == 422:
            logger.warning(f"团队已满，无法邀请: {email}")
            return {"success": False, "message": "团队已满，无法继续邀请"}

        logger.error(f"邀请失败 [{status}]: {resp.text}")
        return {"success": False, "message": f"邀请失败 (HTTP {status})"}
    except Exception as e:
        logger.error(f"请求异常: {e}")
        return {"success": False, "message": f"网络请求失败: {str(e)}"}


@app.route("/")
def index():
    """首页"""
    return send_from_directory("static", "index.html")


@app.route("/api/invite", methods=["POST"])
def api_invite():
    """发送邀请"""
    data = request.get_json()
    if not data or not data.get("email"):
        return jsonify({"success": False, "message": "请输入邮箱地址"}), 400

    email = data["email"].strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"success": False, "message": "邮箱格式不正确"}), 400

    token_status = check_token_status()
    if not token_status["ok"]:
        return jsonify({"success": False, "message": token_status["error"]}), 503

    result = send_invite(token_status["account_id"], email)
    return jsonify(result), 200 if result["success"] else 400


@app.route("/api/health")
def health():
    """健康检查"""
    token_status = check_token_status()
    return jsonify({
        "status": "ok" if token_status["ok"] else "error",
        "token_valid": token_status["ok"],
        "message": token_status.get("error", "服务正常"),
    })


if __name__ == "__main__":
    status = check_token_status()
    if status["ok"]:
        logger.info(f"Token 有效 | 管理员邮箱: {status['email']}")
    else:
        logger.warning(f"Token 问题: {status.get('error', '未知')}")
    logger.info(f"服务启动在端口 {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
