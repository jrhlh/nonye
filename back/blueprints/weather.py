import time
from os import times

from flask import Blueprint, jsonify, request, current_app
import sqlite3
import traceback

bp = Blueprint('weather', __name__, url_prefix='/api/weather')


# 修复数据库查询和结果处理
@bp.route('/data', methods=['GET'])
def get_temperature_data():
    t1 = time.time()
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    if not start_time or not end_time:
        return jsonify({"success": False, "message": "缺少时间参数 (start_time/end_time)"}), 400

    try:
        # 获取数据库连接
        db = current_app.get_db()
        cursor = db.cursor()

        # 执行查询
        query = """
            SELECT 
                device_id,
                timestamp, 
                temperature, 
                humidity 
            FROM temperature_data 
            WHERE timestamp BETWEEN ? AND ? 
            ORDER BY device_id, timestamp ASC
        """
        cursor.execute(query, (start_time, end_time))
        data = cursor.fetchall()

        # 检查查询结果
        if not data:
            print(f"查询无结果: {start_time} 到 {end_time}")
            return jsonify({"success": True, "data": []}), 200

        # 将结果转换为字典列表
        # 修复：使用cursor.description获取列名
        columns = [column[0] for column in cursor.description]
        result = []
        for row in data:
            result.append(dict(zip(columns, row)))

        print(f"查询成功，返回 {len(result)} 条记录")
        t2 = time.time()
        print('111111111111111111111111111111', t2-t1)
        return jsonify({"success": True, "data": result}), 200

    except sqlite3.Error as e:
        db.rollback()
        print(f"数据库错误: {e}")
        traceback.print_exc()  # 打印完整堆栈跟踪
        return jsonify({"success": False, "message": f"数据库操作失败: {str(e)}"}), 500
    except Exception as e:
        print(f"服务器错误: {e}")
        traceback.print_exc()  # 打印完整堆栈跟踪
        return jsonify({"success": False, "message": f"服务器内部错误: {str(e)}"}), 500


@bp.route('/latest', methods=['GET'])
def get_latest_data():
    device_id = request.args.get('device_id', type=int)
    if not device_id:
        return jsonify({"success": False, "message": "缺少设备ID参数 (device_id)"}), 400

    try:
        db = current_app.get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                timestamp, 
                temperature, 
                humidity 
            FROM temperature_data 
            WHERE device_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (device_id,))

        row = cursor.fetchone()
        if not row:
            return jsonify({"success": False, "message": f"设备ID {device_id} 无数据"}), 404

        # 修复：确保结果转换为字典
        columns = [column[0] for column in cursor.description]
        result = dict(zip(columns, row))

        return jsonify({
            "success": True,
            "data": {
                "timestamp": result['timestamp'],  # 假设数据库中已经是字符串格式
                "temperature": result['temperature'],
                "humidity": result['humidity'],
                "device_id": device_id
            }
        }), 200

    except sqlite3.Error as e:
        db.rollback()
        return jsonify({"success": False, "message": f"数据库错误: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500