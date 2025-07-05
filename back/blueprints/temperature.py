from flask import Blueprint, jsonify, request, g
import sqlite3
from datetime import datetime, timedelta

bp = Blueprint('temperature', __name__, url_prefix='/temperature')

# 数据库连接函数 - 新增
def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            'agriculture.db',  # 数据库文件名，请根据实际情况修改
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return g.db

# 关闭数据库连接函数 - 新增
def close_db(e=None):
    """在请求结束时关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# 其他API保持不变...

@bp.route('/daily/average', methods=['GET'])
def get_daily_average_temperature():
    try:
        device_id = request.args.get('deviceId', type=int)
        date = request.args.get('date')

        if not device_id or not date:
            return jsonify({"success": False, "message": "缺少设备ID或日期参数"}), 400

        # 优化日期格式处理
        start_date = f"{date} 00:00:00"
        end_date = f"{date} 23:59:59"

        db = get_db()  # 使用正确的数据库连接函数
        query = '''
        SELECT 
            AVG(temperature) as avg_temperature,
            DATE(timestamp) as date
        FROM temperature_data
        WHERE device_id = ? 
          AND timestamp BETWEEN ? AND ?
        GROUP BY DATE(timestamp)
        '''
        result = db.execute(query, (device_id, start_date, end_date)).fetchone()

        if not result or result['avg_temperature'] is None:
            return jsonify({"success": False, "message": "未找到指定日期的温度数据"}), 404

        response_data = {
            "code": 200,
            "data": {
                "temperatures": [float(result['avg_temperature'])],
                "dates": [result['date']]
            }
        }

        return jsonify(response_data)

    except sqlite3.OperationalError as oe:
        return jsonify({"success": False, "message": f"数据库操作错误: {str(oe)}"}), 500
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": f"数据库错误: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500