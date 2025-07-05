from flask import Blueprint, jsonify, g
import sqlite3

bp = Blueprint('shebei', __name__, url_prefix='/device')

# 修正路由路径，移除空格
@bp.route('/status-statistics', methods=['GET'])
def get_device_status_statistics():
    """
    获取设备状态统计信息，用于饼图展示
    """
    try:
        db = g.get_db()
        cursor = db.execute('''
            SELECT status, COUNT(*) as count
            FROM device
            GROUP BY status
        ''')
        status_counts = cursor.fetchall()
        total_devices = sum([count['count'] for count in status_counts])
        status_percentages = []
        status_color_mapping = {
            'normal': '#4bb118',
            'warning': '#faad14',
            'fault': '#f5222d',
            'offline': '#bfbfbf'
        }
        for status_count in status_counts:
            status = status_count['status']
            percentage = (status_count['count'] / total_devices) * 100
            color = status_color_mapping.get(status, '#bfbfbf')
            status_percentages.append({
                "status": status,
                "percentage": percentage,
                "color": color
            })
        return jsonify({"success": True, "data": status_percentages})
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": f"数据库查询错误: {str(e)}"}), 500

# 修正路由路径，移除空格
@bp.route('/<int:device_id>/temperature-humidity-data', methods=['GET'])
def get_device_temperature_humidity_data(device_id):
    """
    获取指定设备的温湿度数据
    """
    try:
        db = g.get_db()
        cursor = db.execute('''
            SELECT temperature, humidity, timestamp
            FROM temperature_data
            WHERE device_id =?
        ''', (device_id,))
        data = cursor.fetchall()
        result = []
        for row in data:
            result.append({
                "temperature": row['temperature'],
                "humidity": row['humidity'],
                "timestamp": row['timestamp']
            })
        return jsonify({"success": True, "data": result})
    except sqlite3.Error as e:
        return jsonify({"success": False, "message": f"数据库查询错误: {str(e)}"}), 500