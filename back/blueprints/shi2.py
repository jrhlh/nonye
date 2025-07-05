from flask import Blueprint, request, jsonify
import sqlite3
from collections import defaultdict
import traceback

bp = Blueprint('shi2', __name__)


def get_db_connection():
    conn = sqlite3.connect('agriculture.db')
    conn.row_factory = sqlite3.Row
    return conn


@bp.route('/device-moisture', methods=['GET'])
def get_device_moisture_data():
    # 固定查询2025-05-27的数据
    query_date = '2025-05-27'
    start_time = '00:00:00'
    end_time = '23:59:59'

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # 修正表名和字段名，使用temperature_data表中的实际字段
        cur.execute('''
            SELECT device_id, humidity as moisture, timestamp
            FROM temperature_data
            WHERE DATE(timestamp) = ? 
              AND TIME(timestamp) BETWEEN ? AND ?
            ORDER BY device_id, timestamp
        ''', (query_date, start_time, end_time))

        rows = cur.fetchall()

        # 按设备ID分组湿度数据（修正字段引用为humidity）
        device_data = defaultdict(list)
        for row in rows:
            device_id = row['device_id']
            moisture = float(row['moisture'])  # 这里使用别名moisture
            device_data[device_id].append(moisture)

        if not device_data:
            return jsonify({}), 200

        return jsonify(device_data)
    except Exception as e:
        print(f"数据库查询错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': '数据库查询失败，请检查日志'}), 500
    finally:
        conn.close()