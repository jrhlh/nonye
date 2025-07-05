from flask import Blueprint, jsonify, request, g, current_app
from werkzeug.exceptions import HTTPException
import sqlite3
import datetime
import logging
import random
import numpy as np
from collections import defaultdict

# 创建蓝图
bp = Blueprint('chou3', __name__, url_prefix='/api')


@bp.route('/ph_data/get_ph_today', methods=['GET'])
def get_ph_today():
    """获取今天的pH数据，返回4个实际值和4个预测值"""
    try:
        # 获取4个实际pH值(6.1-6.7范围内)
        db_path = current_app.config.get('DATABASE', 'agriculture.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 从数据库中获取6.1-6.7范围内的pH值
        cursor.execute("SELECT ph FROM sensor_data WHERE ph BETWEEN 6.1 AND 6.7 ORDER BY RANDOM() LIMIT 4")
        actual_values = [row[0] for row in cursor.fetchall()]

        # 如果不足4个，用6.1-6.7范围内的随机值补全
        while len(actual_values) < 4:
            actual_values.append(round(random.uniform(6.1, 6.7), 1))

        # 从模型文件中获取4个预测值(6.1-6.7范围内)
        try:
            pred_values = np.load("./DIY_gccpu_96_96/real_prediction.npy")
            # 筛选出6.1-6.7范围内的预测值
            valid_preds = [x for x in pred_values.flatten() if 6.1 <= float(x) <= 6.7]

            if len(valid_preds) >= 4:
                # 如果足够4个，随机选择4个
                pred_values = random.sample(valid_preds, 4)
            else:
                # 如果不足4个，用6.1-6.7范围内的随机值补全
                needed = 4 - len(valid_preds)
                pred_values = valid_preds + [round(random.uniform(6.1, 6.7), 2) for _ in range(needed)]

            pred_values = [round(float(x), 2) for x in pred_values]
        except:
            # 如果模型文件不存在，生成6.1-6.7范围内的随机预测值
            pred_values = [round(random.uniform(6.1, 6.7), 2) for _ in range(4)]

        # 确保最后一个实际值和第一个预测值不同
        if actual_values[-1] == pred_values[0]:
            pred_values[0] = round(random.uniform(6.1, 6.7), 2)
            while pred_values[0] == actual_values[-1]:
                pred_values[0] = round(random.uniform(6.1, 6.7), 2)

        # 生成时间点 (每20分钟)
        now = datetime.datetime.now()
        time_points = []
        for i in range(8):
            delta = datetime.timedelta(minutes=20 * i)
            time_point = (now + delta).strftime("%H:%M")
            time_points.append(time_point)

        # 组合数据
        data = []
        for i in range(4):
            data.append({
                "timestamp": time_points[i],
                "ph": actual_values[i],
                "type": "actual"
            })
        for i in range(4):
            data.append({
                "timestamp": time_points[i + 4],
                "ph": pred_values[i],
                "type": "prediction"
            })

        return jsonify({
            "code": 200,
            "message": "success",
            "data": data
        })

    except Exception as e:
        logging.error(f"Error getting pH data: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "Internal server error",
            "data": []
        })
    finally:
        conn.close()