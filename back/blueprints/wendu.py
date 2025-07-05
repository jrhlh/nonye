import sqlite3
from flask import Blueprint, current_app, jsonify, g, Flask, request
from datetime import datetime, timedelta



# 初始化蓝图对象
bp = Blueprint('wendu', __name__, url_prefix='/api')


@bp.route('/temperature/daily/average', methods=['GET'])
def get_daily_average_by_device():
    """按设备分组获取近30天的每日温度平均值"""
    try:
        db = current_app.get_db()

        # 计算查询日期范围（近30天）
        days = request.args.get('days', default=30, type=int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        current_app.logger.info(f"查询最近{days}天温度数据: {start_date} 至 {end_date}")

        # 执行SQL查询
        cursor = db.execute('''
            SELECT 
                d.id AS device_id,
                d.device_name,
                date(t.timestamp) AS date_day,
                ROUND(AVG(t.temperature), 1) AS avg_temp
            FROM temperature_data t
            JOIN device d ON t.device_id = d.id
            WHERE date(t.timestamp) BETWEEN ? AND ?
            GROUP BY d.id, d.device_name, date_day
            ORDER BY d.id, date_day ASC
        ''', (start_date, end_date))

        rows = cursor.fetchall()
        current_app.logger.info(f"查询结果行数: {len(rows)}")

        if not rows:
            current_app.logger.warning(f"在{start_date}至{end_date}范围内未找到温度数据")
            return jsonify({
                "code": 404,
                "message": f"最近{days}天内无温度数据",
                "data": {}
            })

        # 处理查询结果
        device_data = {}
        for row in rows:
            device_id = str(row['device_id'])
            if device_id not in device_data:
                device_data[device_id] = {
                    'device_name': row['device_name'],
                    'dates': [],
                    'temperatures': []
                }

            device_data[device_id]['dates'].append(row['date_day'])
            device_data[device_id]['temperatures'].append(float(row['avg_temp']))

        # 确保数据按日期排序
        for device in device_data.values():
            if len(device['dates']) > 1:
                combined = sorted(zip(device['dates'], device['temperatures']), key=lambda x: x[0])
                device['dates'], device['temperatures'] = zip(*combined)
                device['dates'] = list(device['dates'])
                device['temperatures'] = list(device['temperatures'])

        return jsonify({
            "code": 200,
            "message": "Success",
            "data": device_data
        })

    except Exception as e:
        current_app.logger.error(f"获取温度数据失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}"
        }), 500

# 注册蓝图

