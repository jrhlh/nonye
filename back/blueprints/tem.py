from flask import Blueprint, jsonify, request, g, current_app
from werkzeug.exceptions import HTTPException
import sqlite3
import datetime

import logging
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('temperature_api')
logger.setLevel(logging.DEBUG)

# 创建蓝图
tem_bp = Blueprint('tem', __name__, url_prefix='/api')


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', 'temperature.db')
        logger.info(f"连接数据库: {db_path}")
        try:
            g.db = sqlite3.connect(
                db_path,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("数据库连接已关闭")


@tem_bp.teardown_app_request
def teardown_request(exception):
    """请求结束时关闭数据库连接"""
    close_db()


@tem_bp.route('/devices', methods=['GET'])
def get_devices():
    """获取所有设备列表（包含设备名称）"""
    try:
        logger.info("获取设备列表请求")
        db = get_db()

        # 查询设备表，获取id和device_name
        cursor = db.execute("SELECT id, device_name FROM device")
        devices = cursor.fetchall()

        # 转换为前端需要的格式 {id: {device_name: name}}
        device_dict = {str(device['id']): {'device_name': device['device_name']} for device in devices}

        logger.info(f"返回设备列表: {len(devices)} 个设备")
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": device_dict
        })
    except Exception as e:
        logger.error(f"获取设备列表失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}"
        }), 500


@tem_bp.route('/temperature/device/<int:device_id>', methods=['GET'])
def get_device_temperature(device_id):
    """获取指定设备在2025-05-25至2025-05-29的温度数据"""
    try:
        logger.info(f"获取设备 {device_id} 温度数据")
        db = get_db()

        # 固定日期范围为2025-05-25至2025-05-29
        start_date = datetime.date(2025, 5, 25)
        end_date = datetime.date(2025, 5, 29)

        logger.info(f"查询日期范围: {start_date} 至 {end_date}")

        # 执行SQL查询
        cursor = db.execute('''
            SELECT 
                date(timestamp) AS date,
                ROUND(AVG(temperature), 1) AS avg_temp
            FROM temperature_data
            WHERE device_id = ? AND date(timestamp) BETWEEN ? AND ?
            GROUP BY date(timestamp)
            ORDER BY date(timestamp) ASC
        ''', (device_id, start_date, end_date))

        rows = cursor.fetchall()
        logger.info(f"查询到 {len(rows)} 条数据")

        # 处理结果
        temperature_data = [
            {
                "date": row['date'],
                "avg_temp": float(row['avg_temp'])
            }
            for row in rows
        ]

        return jsonify({
            "code": 200,
            "message": "Success",
            "data": temperature_data
        })

    except Exception as e:
        logger.error(f"获取温度数据失败: {str(e)}", exc_info=True)
        return jsonify({
            "code": 500,
            "message": f"服务器错误: {str(e)}"
        }), 500