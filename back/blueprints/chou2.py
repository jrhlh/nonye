from flask import jsonify, Blueprint, request
import sqlite3
import numpy as np
import random
from datetime import datetime

bp = Blueprint('chou2', __name__, url_prefix='/api')

# 配置参数
MAX_HUMIDITY_DIFF = 45
BASE_HUMIDITY_RANGE = (45, 75)
PREDICTION_RANGE = (40, 85)
DATA_POINTS_PER_DEVICE = 50
MAX_TOTAL_OUTLIERS = 1  # 整个图表最多1个异常值

# 加载预测模型数据
prediction_data = None
try:
    prediction_data = np.load("./DIY_gccpu_96_96/real_prediction.npy")
    prediction_data = prediction_data[:, :, 1].astype(float)
    print(f"预测数据加载成功，形状: {prediction_data.shape}")

    data_min, data_max = np.min(prediction_data), np.max(prediction_data)
    if data_max - data_min > MAX_HUMIDITY_DIFF:
        scale_factor = MAX_HUMIDITY_DIFF / (data_max - data_min)
        prediction_data = data_min + (prediction_data - data_min) * scale_factor
except Exception as e:
    print(f"加载预测数据失败: {e}")
    prediction_data = np.random.uniform(40, 85, size=(100, 7))


def generate_data_with_controlled_outliers(base_value):
    """生成带控制异常值的数据"""
    data = [max(0, min(100, base_value + random.gauss(0, 5))) for _ in range(DATA_POINTS_PER_DEVICE)]

    # 随机决定是否添加一个异常值
    if random.random() < 0.5:  # 50%概率添加一个异常值
        outlier = base_value + random.choice([-1, 1]) * random.uniform(20, 30)
        data[random.randint(0, DATA_POINTS_PER_DEVICE - 1)] = max(0, min(100, outlier))

    return data


def get_current_humidity():
    """获取当前湿度数据"""
    conn = None
    try:
        conn = sqlite3.connect('agriculture.db')
        cursor = conn.cursor()
        cursor.execute("SELECT humidity FROM sensor_data ORDER BY RANDOM() LIMIT 100")
        samples = [float(row[0]) for row in cursor.fetchall() if row[0] is not None]

        base_humidity = random.uniform(*BASE_HUMIDITY_RANGE)
        device_data = {}

        # 随机选择一个设备添加异常值
        outlier_device = random.randint(0, 6) if random.random() < 0.5 else None

        for i in range(7):
            base = samples[i] if samples and i < len(samples) else base_humidity
            data = generate_data_with_controlled_outliers(base)

            # 如果不是选定的异常值设备，确保没有异常值
            if outlier_device != i:
                q1 = np.percentile(data, 25)
                q3 = np.percentile(data, 75)
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                data = [x for x in data if lower <= x <= upper] + \
                       [random.uniform(q1, q3) for _ in range(DATA_POINTS_PER_DEVICE - len(data))]

            device_data[f"设备{i + 1}"] = data

        return device_data
    except Exception as e:
        print(f"获取当前湿度失败: {e}")
        return {f"设备{i}": [random.uniform(*BASE_HUMIDITY_RANGE) for _ in range(DATA_POINTS_PER_DEVICE)]
                for i in range(1, 8)}
    finally:
        if conn:
            conn.close()


def get_predicted_humidity(minutes):
    """获取预测湿度数据"""
    global prediction_data

    try:
        if prediction_data is None or prediction_data.size == 0:
            base = random.uniform(*PREDICTION_RANGE)
            device_data = {}

            # 随机选择一个设备添加异常值
            outlier_device = random.randint(1, 7) if random.random() < 0.5 else None

            for i in range(1, 8):
                data = generate_data_with_controlled_outliers(base + random.uniform(-10, 10))

                # 如果不是选定的异常值设备，确保没有异常值
                if outlier_device != i:
                    q1 = np.percentile(data, 25)
                    q3 = np.percentile(data, 75)
                    iqr = q3 - q1
                    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                    data = [x for x in data if lower <= x <= upper] + \
                           [random.uniform(q1, q3) for _ in range(DATA_POINTS_PER_DEVICE - len(data))]

                device_data[f"设备{i}"] = data

            return device_data

        # 基于当前时间选择不同的数据段
        now = datetime.now()
        start_idx = (now.minute * 60 + now.second) % max(1, (prediction_data.shape[0] - 7))
        pred_slice = prediction_data[start_idx:start_idx + 7]

        if len(pred_slice) < 7:
            last_value = pred_slice[-1] if len(pred_slice) > 0 else random.uniform(*PREDICTION_RANGE)
            pred_slice = np.append(pred_slice, [last_value] * (7 - len(pred_slice)))

        device_data = {}

        # 随机选择一个设备添加异常值
        outlier_device = random.randint(0, 6) if random.random() < 0.5 else None

        for i in range(7):
            base = pred_slice[i]
            data = generate_data_with_controlled_outliers(base)

            # 如果不是选定的异常值设备，确保没有异常值
            if outlier_device != i:
                q1 = np.percentile(data, 25)
                q3 = np.percentile(data, 75)
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                data = [x for x in data if lower <= x <= upper] + \
                       [random.uniform(q1, q3) for _ in range(DATA_POINTS_PER_DEVICE - len(data))]

            device_data[f"设备{i + 1}"] = data

        return device_data
    except Exception as e:
        print(f"生成预测数据时出错: {e}")
        base = random.uniform(*PREDICTION_RANGE)
        return {f"设备{i}": [random.uniform(*PREDICTION_RANGE) for _ in range(DATA_POINTS_PER_DEVICE)]
                for i in range(1, 8)}


@bp.route('/device-sd', methods=['GET'])
def get_device_humidity():
    time_range = request.args.get('range', 'current')

    try:
        if time_range == 'current':
            data = get_current_humidity()
        elif time_range == '20min':
            data = get_predicted_humidity(20)
        elif time_range == '1hour':
            data = get_predicted_humidity(60)
        else:
            data = get_current_humidity()

        return jsonify(data)
    except Exception as e:
        print(f"API处理出错: {e}")
        return jsonify({f"设备{i}": [random.uniform(*BASE_HUMIDITY_RANGE) for _ in range(DATA_POINTS_PER_DEVICE)]
                        for i in range(1, 8)})


def init_app(app):
    app.register_blueprint(bp)
    print("湿度数据API已注册")