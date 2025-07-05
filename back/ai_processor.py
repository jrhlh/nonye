import websocket
import json
import hmac
import hashlib
import base64
import time
import ssl
from urllib.parse import urlencode
import datetime
from threading import Lock
from flask import current_app

# 全局处理状态锁
status_lock = Lock()
processing_status = {}

def process_ai_message(appid, api_key, api_secret, spark_url, domain, messages):
    """处理AI消息并返回回答，优化超时处理和错误处理"""
    max_retries = 3
    retries = 0
    last_error = None

    while retries < max_retries:
        try:
            # 生成认证URL
            url = generate_auth_url(spark_url, api_key, api_secret)

            # 创建WebSocket连接，设置超时为30秒
            ws = websocket.create_connection(
                url,
                sslopt={"cert_reqs": ssl.CERT_NONE},
                timeout=30
            )

            # 准备请求数据
            request_data = {
                "header": {
                    "app_id": appid,
                    "uid": f"user_{int(time.time())}_{retries}"
                },
                "parameter": {
                    "chat": {
                        "domain": domain,
                        "temperature": 0.7,
                        "max_tokens": 2048,
                        "top_k": 3
                    }
                },
                "payload": {
                    "message": {
                        "text": messages
                    }
                }
            }

            # 发送请求
            ws.send(json.dumps(request_data))

            # 接收响应
            answer = ""
            start_time = time.time()
            while True:
                try:
                    response = ws.recv()
                    if not response:
                        break

                    data = json.loads(response)
                    if "payload" in data and "choices" in data["payload"]:
                        if "text" in data["payload"]["choices"]:
                            for item in data["payload"]["choices"]["text"]:
                                if "content" in item:
                                    answer += item["content"]

                    # 检查是否是最后一条消息
                    if "header" in data and "status" in data["header"] and data["header"]["status"] == 2:
                        break

                    # 超时检查（45秒超时）
                    if time.time() - start_time > 45:
                        current_app.logger.warning("AI接口响应超时")
                        raise TimeoutError("AI接口响应超时")

                except websocket.WebSocketTimeoutException:
                    current_app.logger.warning("WebSocket接收超时")
                    raise TimeoutError("WebSocket接收超时")

            # 关闭连接
            ws.close()

            # 检查回答是否有效
            if answer.strip():
                return answer

            retries += 1
            last_error = "AI返回空回答"
            current_app.logger.warning(f"AI返回空回答，重试 {retries}/{max_retries}")

        except TimeoutError as te:
            retries += 1
            last_error = str(te)
            current_app.logger.error(f"AI接口超时 ({retries}/{max_retries}): {str(te)}")
            if ws:
                try:
                    ws.close()
                except:
                    pass
        except websocket.WebSocketException as we:
            retries += 1
            last_error = str(we)
            current_app.logger.error(f"WebSocket错误 ({retries}/{max_retries}): {str(we)}")
        except Exception as e:
            retries += 1
            last_error = str(e)
            current_app.logger.error(f"处理错误 ({retries}/{max_retries}): {str(e)}")
            if ws:
                try:
                    ws.close()
                except:
                    pass

    return f"抱歉，AI处理失败: {last_error or '未知错误'}"

def generate_auth_url(api_url, api_key, api_secret):
    """生成认证URL"""
    from urllib.parse import urlparse
    url = urlparse(api_url)
    host = url.netloc
    path = url.path

    # 生成RFC1123格式的时间戳
    now = time.time()
    date = datetime.datetime.fromtimestamp(now, datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    # 构建签名原始字符串
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

    # 计算HMAC-SHA256签名
    signature_sha = hmac.new(
        api_secret.encode('utf-8'),
        signature_origin.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # Base64编码
    signature_sha_base64 = base64.b64encode(signature_sha).decode()

    # 构建认证字符串
    authorization_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature_sha_base64}"'
    )

    # Base64编码认证字符串
    authorization = base64.b64encode(authorization_origin.encode()).decode()

    # 构建最终URL
    query_params = {
        'authorization': authorization,
        'date': date,
        'host': host
    }

    return f"{api_url}?{urlencode(query_params)}"