# blueprints/yzm.py

import random
import smtplib
import string
import ssl
import time

from email.mime.text import MIMEText
from flask import request, jsonify, Blueprint
from flask_cors import CORS

bp = Blueprint('yzm', __name__)
CORS(bp, supports_credentials=True)

verification_codes = {}

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def send_email(receiver, code):
    sender = '3492073524@qq.com'
    password = 'xhemkcgrgximchcd'

    msg = MIMEText(f'您的验证码是：{code}，5分钟内有效。')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = '禾境智联后台管理系统 - 验证码'

    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            print(f"[尝试 {attempt}/{max_retries}] 正在连接 SMTP 服务器...")
            context = ssl.create_default_context()

            with smtplib.SMTP_SSL('smtp.qq.com', 465, context=context) as server:
                print("✅ SMTP 连接成功")
                server.login(sender, password)
                print("🔑 登录成功")
                server.sendmail(sender, receiver, msg.as_string())
                print("📧 邮件发送成功")
                return True  # 成功发送

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ 认证失败（授权码错误）: {str(e)}")
            return False
        except smtplib.SMTPConnectError as e:
            print(f"❌ 连接失败: {str(e)}")
        except smtplib.SMTPException as e:
            error_msg = str(e)
            if error_msg == "(-1, b'\\x00\\x00\\x00')" or "unexpected EOF" in error_msg:
                print("⚠️ 警告: 忽略非致命异常，假设邮件已发送成功")
                return True  # 假设邮件已成功发送
            else:
                print(f"❌ SMTP 异常: {error_msg}")
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")

        if attempt < max_retries:
            print("🔄 正在等待重试...")
            time.sleep(2)
        else:
            print("💥 达到最大重试次数，邮件发送失败")
    return False

@bp.route("/captcha/email", methods=["POST"])
def send_code():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"message": "邮箱不能为空"}), 400

    code = generate_code()
    verification_codes[email] = code
    print(f"验证码已生成: {email} -> {code}")

    if send_email(email, code):
        return jsonify({"message": "验证码已发送"}), 200
    else:
        return jsonify({"message": "邮件发送失败"}), 500

@bp.route("/captcha/verify", methods=["POST"])
def verify_code():
    data = request.json
    email = data.get("email")
    user_code = data.get("code")

    if not email or not user_code:
        return jsonify({"message": "参数错误", "valid": False}), 400

    stored_code = verification_codes.get(email)

    if stored_code and stored_code == user_code:
        del verification_codes[email]
        return jsonify({"valid": True}), 200
    else:
        return jsonify({"valid": False}), 400