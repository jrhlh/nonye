from flask import Blueprint, request, jsonify, current_app
import logging

bp = Blueprint('register', __name__)
logger = logging.getLogger(__name__)
FRONTEND_ORIGIN = 'http://localhost:5173'

@bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', FRONTEND_ORIGIN)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200

    try:
        logger.info("收到注册请求")
        data = request.get_json()
        if not data:
            return jsonify({'message': '请求数据为空'}), 400

        username = data.get('username')
        password = data.get('password')
        if not all([username, password]):
            return jsonify({'message': '缺少用户名或密码'}), 400

        db = current_app.get_db()
        cursor = db.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({'message': '用户名已存在'}), 400

        # 插入数据时包含 permission_level（默认设为 Operator）
        cursor.execute(
            "INSERT INTO user (username, password, permission_level) VALUES (?, ?, ?)",
            (username, password, 'Operator')
        )
        db.commit()

        logger.info(f"用户 {username} 注册成功")
        return jsonify({'message': '注册成功'}), 201

    except Exception as e:
        logger.error(f"服务器内部错误: {str(e)}", exc_info=True)
        db.rollback()
        return jsonify({'message': '服务器内部错误'}), 500