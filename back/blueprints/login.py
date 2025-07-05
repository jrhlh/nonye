from flask import Blueprint, request, jsonify, make_response, current_app
import datetime
import os
import logging
import base64
import json
import hashlib
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)


# 添加 CORS 头
def add_cors_headers(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response


# 辅助函数：创建JWT令牌
def create_jwt_token(payload, secret_key, algorithm="HS256", expires_in=7200):
    # 添加过期时间
    payload_with_exp = payload.copy()
    payload_with_exp["exp"] = int((datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)).timestamp())

    # JWT头部
    header = {"alg": algorithm, "typ": "JWT"}

    # 编码头部和载荷
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode('utf-8')).rstrip(b'=').decode('utf-8')
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload_with_exp).encode('utf-8')).rstrip(b'=').decode(
        'utf-8')

    # 组合头部和载荷
    message = f"{encoded_header}.{encoded_payload}"

    # 创建签名
    if algorithm == "HS256":
        # 使用HMAC-SHA256创建签名
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode('utf-8')
    elif algorithm == "RS256":
        # 使用RSA-SHA256创建签名 (生产环境中应妥善管理私钥)
        private_key = serialization.load_pem_private_key(
            secret_key.encode('utf-8'),
            password=None
        )
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode('utf-8')
    else:
        raise ValueError(f"不支持的算法: {algorithm}")

    # 组合JWT
    jwt_token = f"{encoded_header}.{encoded_payload}.{encoded_signature}"
    return jwt_token


@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == "OPTIONS":
        return add_cors_headers(make_response())

    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            logger.warning("登录请求缺少必要字段")
            response = jsonify({'message': '缺少必要字段'})
            return add_cors_headers(response), 400

        # 获取数据库连接
        db = current_app.get_db()
        cursor = db.cursor()

        # 查询用户（注意：生产环境应使用参数化查询防止SQL注入）
        cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
        user_row = cursor.fetchone()

        if not user_row:
            logger.warning(f"用户不存在: {username}")
            response = jsonify({'message': '用户不存在'})
            return add_cors_headers(response), 401

        # 将元组结果转换为字典（如果需要）
        if isinstance(user_row, tuple):
            user_dict = dict(zip([column[0] for column in cursor.description], user_row))
        else:
            user_dict = user_row

        # 明文密码比对（⚠️ 不推荐用于生产环境）
        if password != user_dict['password']:
            logger.warning(f"密码错误: {username}")
            response = jsonify({'message': '密码错误'})
            return add_cors_headers(response), 401

        # 检查用户状态
        if user_dict['status'] != 'Active':
            logger.warning(f"用户已禁用: {username}")
            response = jsonify({'message': '用户已禁用'})
            return add_cors_headers(response), 403

        # 判断是否为管理员（基于permission_level字段）
        is_admin = user_dict['permission_level'] == 'Admin'

        # 构建 JWT Token
        secret_key = os.getenv('SECRET_KEY', '默认密钥')  # 建议设置环境变量

        # 使用我们自己的函数创建JWT
        token = create_jwt_token(
            {
                'user_id': user_dict['id'],
                'username': user_dict['username'],
                'is_admin': is_admin,
            },
            secret_key,
            algorithm="HS256",
            expires_in=2 * 60 * 60  # 2小时
        )

        response_data = jsonify({
            'success': True,
            'message': '登录成功',
            'username': user_dict['username'],
            'is_admin': is_admin,
            'user_id': user_dict['id']  # 可选：返回用户ID
        })

        response = add_cors_headers(response_data)

        # 设置 Cookie（注意：生产环境应启用 secure=True）
        response.set_cookie(
            'token',
            value=token,
            max_age=2 * 60 * 60,  # 2小时
            httponly=True,
            samesite='None',
            secure=False  # 开发环境使用False，生产环境使用True
        )

        logger.info(f"用户登录成功: {username}")
        return response, 200

    except Exception as e:
        logger.error(f"登录过程发生错误: {str(e)}", exc_info=True)
        response = jsonify({'message': '服务器内部错误'})
        return add_cors_headers(response), 500
