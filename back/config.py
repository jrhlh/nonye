import os
from datetime import timedelta

# session配置
SECRET_KEY = os.urandom(24)  # 设置秘钥
PERMANENT_SESSION_LIFETIME = timedelta(days=10)  # 设置session生命周期

# config.py
APPID = "2dbd6b09"
API_KEY = "df4e4c0b3526cff5f0a1160be5e03106"
API_SECRET = "OWQ3NGZhYWNmMTQ4ZmUyZDc3MzkwODY4"
SPARK_URL = "wss://spark-api.xf-yun.com/v1/x1"
DOMAIN = "x1"