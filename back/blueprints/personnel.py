from flask import Blueprint, request, jsonify, g, current_app
import sqlite3
from datetime import datetime

bp = Blueprint('personnel', __name__, url_prefix='/personnel')

# 定义全局有效的权限级别
VALID_PERMISSIONS = {'Admin', 'Supervisor', 'Operator'}

# 数据库连接
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            check_same_thread=False
        )
        g.db.row_factory = sqlite3.Row
    return g.db

# 关闭数据库连接
@bp.teardown_request
def close_db_connection(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 创建表（初始化数据库）
@bp.cli.command('init-db')
def init_db():
    schema = """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        permission_level TEXT NOT NULL CHECK (permission_level IN ('Admin', 'Supervisor', 'Operator')),
        hire_date TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT DEFAULT 'Active',
        linked_devices INTEGER DEFAULT 0,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS operation_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (id)
    );
    """
    with current_app.open_resource('schema.sql', mode='w') as f:
        f.write(schema)
    get_db().executescript(schema)
    print("数据库初始化完成")

# 用户列表接口
@bp.route('/users', methods=['GET'])
def get_users():
    try:
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT 
                id,
                username,
                email,
                phone,
                permission_level,
                DATE(hire_date) AS hire_date,
                status,
                linked_devices
            FROM user
            ORDER BY 
                CASE permission_level 
                    WHEN 'Admin' THEN 1
                    WHEN 'Supervisor' THEN 2
                    WHEN 'Operator' THEN 3
                END, 
                hire_date DESC
        """
        filter_permission = request.args.get('filter_permission')
        if filter_permission and filter_permission != 'all':
            cursor.execute(query + " WHERE permission_level = ?", (filter_permission,))
        else:
            cursor.execute(query)
        users = cursor.fetchall()
        return jsonify({
            'code': 200,
            'data': [dict(user) for user in users]
        })
    except sqlite3.Error as e:
        current_app.logger.error(f"获取用户列表错误: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# 添加用户接口
@bp.route('/users', methods=['POST'])
def add_user():
    data = request.json
    # 明确必填字段（包括 password）
    required_fields = ['username', 'permissionLevel', 'hire_date', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'code': 400,
                'message': f'缺少必填字段: {field}'
            }), 400

    permission = data['permissionLevel']
    if permission not in VALID_PERMISSIONS:  # 修改：使用全局常量
        current_app.logger.error(f"无效权限级别: {data['permissionLevel']}")
        return jsonify({
            'code': 400,
            'message': '权限级别格式错误，请使用Admin、Supervisor或Operator'
        }), 400

    try:
        db = get_db()
        cursor = db.cursor()
        # 插入所有字段（包括 email、phone）
        cursor.execute(
            """INSERT INTO user (
                username, 
                password, 
                permission_level, 
                hire_date, 
                email, 
                phone
            ) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(username) DO NOTHING""",
            (
                data['username'],
                data['password'],
                permission,
                data['hire_date'],
                data.get('email', ''),  # 允许为空
                data.get('phone', '')   # 允许为空
            )
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({
                'code': 400,
                'message': '用户名已存在'
            }), 400

        # 记录操作日志
        cursor.execute(
            "INSERT INTO operation_log (user_id, type, message) VALUES (?, ?, ?)",
            (cursor.lastrowid, 'USER_CREATE', f'创建用户 {data["username"]}')
        )
        db.commit()

        return jsonify({
            'code': 201,
            'message': '用户创建成功'
        }), 201

    except sqlite3.IntegrityError as e:
        if 'CHECK constraint failed' in str(e):
            return jsonify({
                'code': 400,
                'message': '权限级别格式错误，请使用Admin、Supervisor或Operator'
            }), 400
        else:
            current_app.logger.error(f"添加用户错误: {str(e)}")
            db.rollback()
            return jsonify({
                'code': 500,
                'message': '服务器内部错误'
            }), 500
    except sqlite3.Error as e:
        current_app.logger.error(f"添加用户错误: {str(e)}")
        db.rollback()
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

# 编辑用户接口
@bp.route('/users/<string:username>', methods=['PUT'])
def edit_user(username):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return jsonify({
            'code': 404,
            'message': '用户不存在'
        }), 404

    update_fields = []
    params = []

    # 处理权限级别
    if 'permissionLevel' in data:
        permission = data['permissionLevel']
        if permission not in VALID_PERMISSIONS:  # 修改：使用全局常量
            return jsonify({
                'code': 400,
                'message': '权限级别格式错误，请使用Admin、Supervisor或Operator'
            }), 400
        update_fields.append("permission_level = ?")
        params.append(permission)

    # 处理其他字段
    if 'hire_date' in data:
        update_fields.append("hire_date = ?")
        params.append(data['hire_date'])
    if 'linkedDevices' in data:
        update_fields.append("linked_devices = ?")
        params.append(data['linkedDevices'])
    if 'status' in data:
        update_fields.append("status = ?")
        params.append(data['status'])
    if 'email' in data:
        update_fields.append("email = ?")
        params.append(data['email'])
    if 'phone' in data:
        update_fields.append("phone = ?")
        params.append(data['phone'])
    if 'password' in data:  # 允许修改密码
        update_fields.append("password = ?")
        params.append(data['password'])

    if not update_fields:
        return jsonify({
            'code': 400,
            'message': '未提供更新字段'
        }), 400

    params.append(username)
    query = f"UPDATE user SET {', '.join(update_fields)} WHERE username = ?"
    try:
        cursor.execute(query, params)
        db.commit()

        # 记录操作日志
        cursor.execute(
            "INSERT INTO operation_log (user_id, type, message) VALUES (?, ?, ?)",
            (user['id'], 'USER_UPDATE', f'更新用户 {username}')
        )
        db.commit()

        return jsonify({
            'code': 200,
            'message': '更新成功'
        }), 200

    except sqlite3.Error as e:
        current_app.logger.error(f"编辑用户错误: {str(e)}")
        db.rollback()
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

# 删除用户接口
@bp.route('/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM user WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return jsonify({
            'code': 404,
            'message': '用户不存在'
        }), 404

    if username == 'root':
        return jsonify({
            'code': 403,
            'message': '禁止删除root用户'
        }), 403

    try:
        cursor.execute("DELETE FROM user WHERE username = ?", (username,))
        db.commit()

        # 记录操作日志
        cursor.execute(
            "INSERT INTO operation_log (user_id, type, message) VALUES (?, ?, ?)",
            (user['id'], 'USER_DELETE', f'删除用户 {username}')
        )
        db.commit()

        return jsonify({
            'code': 200,
            'message': '用户删除成功'
        }), 200

    except sqlite3.Error as e:
        current_app.logger.error(f"删除用户错误: {str(e)}")
        db.rollback()
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500

# 操作日志接口
@bp.route('/logs', methods=['GET'])
def get_logs():
    try:
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT 
                id,
                strftime('%Y-%m-%d %H:%M:%S', timestamp) AS timestamp,
                type,
                message,
                (SELECT username FROM user WHERE id = user_id) AS user
            FROM operation_log
            ORDER BY timestamp DESC  -- 按时间降序排列
        """
        cursor.execute(query)
        logs = cursor.fetchall()
        return jsonify({
            'code': 200,
            'data': [dict(log) for log in logs]
        })
    except sqlite3.Error as e:
        current_app.logger.error(f"获取日志错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '服务器内部错误'
        }), 500