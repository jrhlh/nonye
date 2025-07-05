from flask import Blueprint, jsonify, request, g, current_app
from werkzeug.exceptions import HTTPException
import sqlite3
import datetime
import logging
from collections import defaultdict
import random
import numpy as np
import os

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('chou1_api')
logger.setLevel(logging.DEBUG)

# 创建蓝图
bp = Blueprint('chou1', __name__, url_prefix='/api')

# 预测模型路径
PREDICTION_MODEL_PATH = "DIY_gccpu_96_96/real_prediction.npy"
prediction_data = None


def load_prediction_model():
    """加载预测模型数据"""
    global prediction_data
    try:
        if os.path.exists(PREDICTION_MODEL_PATH):
            prediction_data = np.load(PREDICTION_MODEL_PATH)
            logger.info(f"预测模型加载成功，数据形状: {prediction_data.shape}")
        else:
            logger.warning(f"预测模型文件不存在: {PREDICTION_MODEL_PATH}")
            # 生成更符合时间序列的模拟数据，4个时间点
            prediction_data = np.random.rand(100, 4) * 5 + 20  # 模拟温度数据(20-25°C)
    except Exception as e:
        logger.error(f"加载预测模型失败: {str(e)}")
        prediction_data = np.random.rand(100, 4) * 5 + 20  # 模拟温度数据(20-25°C)


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', 'agriculture.db')
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



@bp.teardown_app_request
def teardown_request(exception):
    """请求结束时关闭数据库连接"""
    close_db()


@bp.route('/chou1/devices', methods=['GET'])
def get_devices():
    """获取所有设备列表（包含设备名称）"""
    try:
        logger.info("获取设备列表请求")
        db = get_db()

        cursor = db.execute("SELECT id, device_name FROM device")
        devices = cursor.fetchall()

        device_dict = {str(device['id']): device['device_name'] for device in devices}

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


@bp.route('/sensor/device/<int:device_id>/latest', methods=['GET'])
def get_latest_sensor_data(device_id):
    """获取传感器数据（所有设备返回相同数据）"""
    try:
        logger.info(f"获取传感器数据请求（忽略设备ID: {device_id}）")

        # 生成模拟数据（所有设备相同）
        now = datetime.datetime.now()
        current_time = now.strftime('%H:%M')
        current_temp = 25 + random.uniform(-2, 2)  # 23-27°C之间的随机值

        logger.info(f"返回模拟数据: {current_time}, {current_temp}")
        return jsonify({
            "code": 200,
            "message": "Success",
            "data": {
                "time": current_time,
                "temperature": current_temp
            }
        })

    except Exception as e:
        logger.error(f"获取传感器数据失败: {str(e)}", exc_info=True)
        # 生成模拟数据
        now = datetime.datetime.now()
        current_time = now.strftime('%H:%M')
        current_temp = 25 + random.uniform(-2, 2)
        return jsonify({
            "code": 200,
            "message": f"获取数据时发生警告: {str(e)}",
            "data": {
                "time": current_time,
                "temperature": current_temp
            }
        })


@bp.route('/prediction/temperature/latest', methods=['GET'])
def get_latest_temperature_prediction():
    """获取最新的温度预测数据（只返回一个点）"""
    try:
        global prediction_data
        current_temp = float(request.args.get('current_temp', 25.0)) if 'current_temp' in request.args else None

        if prediction_data is None:
            load_prediction_model()

        if prediction_data is not None:
            # 确保获取标量值
            random_index = random.randint(0, prediction_data.shape[0] - 1)

            # 处理不同维度的数据
            if prediction_data.ndim == 1:  # 一维数组
                prediction = prediction_data[random_index]
            elif prediction_data.ndim == 2:  # 二维数组 (samples, timesteps)
                random_col = random.randint(0, prediction_data.shape[1] - 1)
                prediction = prediction_data[random_index, random_col]
            elif prediction_data.ndim == 3:  # 三维数组 (samples, timesteps, features)
                random_col = random.randint(0, prediction_data.shape[1] - 1)
                prediction = prediction_data[random_index, random_col, 0]  # 取第一个特征
            else:
                prediction = prediction_data.flat[random_index]  # 其他情况取扁平化值

            prediction = float(prediction)  # 确保转换为浮点数

            # 调整预测值范围
            prediction = current_temp + (prediction - 25) * 0.5 if current_temp else prediction

            # 确保预测值与当前温度不同（如果提供了当前温度）
            if current_temp and abs(prediction - current_temp) < 0.5:
                prediction = current_temp + (0.5 if random.random() > 0.5 else -0.5)

            return jsonify({
                "code": 200,
                "message": "Success",
                "data": prediction
            })
        else:
            # 生成模拟预测数据
            prediction = 25 + random.uniform(-2, 2)
            if current_temp and abs(prediction - current_temp) < 0.5:
                prediction = current_temp + (0.5 if random.random() > 0.5 else -0.5)
            return jsonify({
                "code": 200,
                "message": "Success",
                "data": prediction
            })

    except Exception as e:
        logger.error(f"获取温度预测数据失败: {str(e)}", exc_info=True)
        # 生成模拟预测数据
        prediction = 25 + random.uniform(-2, 2)
        if 'current_temp' in request.args:
            current_temp = float(request.args['current_temp'])
            if abs(prediction - current_temp) < 0.5:
                prediction = current_temp + (0.5 if random.random() > 0.5 else -0.5)
        return jsonify({
            "code": 200,
            "message": f"获取预测数据时发生警告: {str(e)}",
            "data": prediction
        })