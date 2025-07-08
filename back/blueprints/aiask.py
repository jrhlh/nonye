from flask import Blueprint, request, jsonify, current_app
import json
import datetime
import threading
import time
from werkzeug.exceptions import BadRequest, InternalServerError
from ai_processor import process_ai_message
import uuid

bp = Blueprint('aiask', __name__)

# 使用字典存储对话历史和状态
conversation_data = {}
data_lock = threading.Lock()

# 农业顾问AI系统提示词
SYSTEM_PROMPT = """你是一个专业的农业知识与设备管理顾问 AI，专注于农业生产知识解答与农业设备状态管理指导，尤其擅长为种植户、养殖户及农业生产企业提供实用建议。

你的任务是：
1. 解答农业生产相关的知识疑问，包括但不限于作物种植、畜禽养殖、病虫害防治、土壤改良、农资使用等内容。
2. 提供农业设备（如播种机、收割机、灌溉设备、养殖设备等）的状态监测、日常维护、常见故障排查及管理建议。
3. 鼓励用户采用科学的农业生产方式和规范的设备管理流程，提升生产效率与安全性。

你需要遵循的原则：
- 始终保持专业、严谨、科学的态度，基于农业技术规范和设备管理标准提供建议。
- 不提供未经证实的农业技术或设备操作方法，对于复杂的设备故障或特殊农业问题，建议用户咨询专业技术人员或农业机构。
- 只返回相关建议，不要返回其他无关内容"""


def get_conversation_data(user_id):
    """获取用户的对话数据"""
    with data_lock:
        if user_id not in conversation_data:
            conversation_data[user_id] = {
                'history': [],
                'processing': False,
                'last_active': time.time(),
                'request_id': None
            }
        return conversation_data[user_id]


def cleanup_inactive_sessions():
    """清理超过1小时不活跃的会话"""
    with data_lock:
        current_time = time.time()
        inactive_users = [
            user_id for user_id, data in conversation_data.items()
            if current_time - data['last_active'] > 3600  # 1小时
        ]
        for user_id in inactive_users:
            del conversation_data[user_id]


def add_to_history(user_id, role, content):
    """添加消息到对话历史，确保内容不为空"""
    data = get_conversation_data(user_id)
    data['history'].append({
        "role": role,
        "content": content or "（空回复）",
        "timestamp": datetime.datetime.now().isoformat()
    })
    data['last_active'] = time.time()

    # 限制历史记录长度（仅保留最近10条交互）
    if len(data['history']) > 10:
        data['history'] = data['history'][-10:]


def format_question(history):
    """格式化问题，包含系统提示和历史对话"""
    # 获取最近的历史记录（最多10条交互）
    recent_history = history[-10:] if len(history) > 10 else history

    # 构建包含系统提示的完整对话上下文
    formatted_context = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # 添加用户与助手的历史对话
    formatted_context.extend([
        {"role": msg["role"], "content": msg["content"]}
        for msg in recent_history
    ])

    return formatted_context


@bp.route('/ask', methods=['POST'])
def ask():
    """向AI提问，改进异步处理流程"""
    data = request.json
    question = data.get('question')
    user_id = data.get('user_id', 'anonymous')

    if not question:
        return jsonify({"code": 400, "message": "问题不能为空"}), 400

    # 获取用户数据
    user_data = get_conversation_data(user_id)

    # 检查是否已有处理中的请求
    if user_data['processing']:
        return jsonify({
            "code": 429,
            "message": "已有处理中的请求，请稍后再试",
            "request_id": user_data['request_id']
        }), 429

    # 添加用户问题到历史
    add_to_history(user_id, "user", question)

    # 格式化问题（包含系统提示和历史对话）
    full_question = format_question(user_data['history'])

    # 生成唯一请求ID
    request_id = f"req_{uuid.uuid4().hex[:8]}"
    user_data['request_id'] = request_id
    user_data['processing'] = True

    # 调用AI回答函数（异步处理）
    try:
        appid = current_app.config.get('APPID')
        api_key = current_app.config.get('API_KEY')
        api_secret = current_app.config.get('API_SECRET')
        spark_url = current_app.config.get('SPARK_URL')
        domain = current_app.config.get('DOMAIN', 'x1')

        app = current_app._get_current_object()

        def process_ai_request():
            try:
                with app.app_context():
                    start_time = time.time()
                    current_app.logger.info(f"开始处理AI请求 {request_id}")

                    ai_answer = process_ai_message(
                        appid, api_key, api_secret, spark_url, domain, full_question
                    )

                    # 记录处理时间
                    process_time = time.time() - start_time
                    current_app.logger.info(
                        f"AI请求 {request_id} 处理完成，耗时 {process_time:.2f}秒"
                    )

                    add_to_history(user_id, "assistant", ai_answer)
            except Exception as e:
                with app.app_context():
                    current_app.logger.error(f"AI请求 {request_id} 处理错误: {str(e)}")
                    add_to_history(user_id, "assistant", f"处理请求时出错: {str(e)}")
            finally:
                # 更新处理状态
                user_data['processing'] = False
                user_data['request_id'] = None
                cleanup_inactive_sessions()

        # 启动处理线程
        threading.Thread(target=process_ai_request, daemon=True).start()

        return jsonify({
            "code": 200,
            "message": "请求已接收，正在处理中",
            "request_id": request_id
        })

    except Exception as e:
        user_data['processing'] = False
        user_data['request_id'] = None
        current_app.logger.error(f"AI请求初始化错误: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "服务器内部错误",
            "request_id": request_id
        }), 500


@bp.route('/history', methods=['GET'])
def get_history():
    """获取对话历史，优化性能"""
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({
            "code": 400,
            "message": "用户ID不能为空",
            "history": []
        }), 400

    try:
        user_data = get_conversation_data(user_id)
        history = user_data.get('history', [])

        current_app.logger.info(
            f"获取历史记录，用户ID: {user_id}，记录数量: {len(history)}"
        )

        return jsonify({
            "code": 200,
            "message": "获取历史记录成功",
            "history": history,
            "processing": user_data['processing'],
            "request_id": user_data['request_id']
        })
    except Exception as e:
        current_app.logger.error(f"获取历史记录错误: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "获取历史记录失败",
            "history": []
        }), 500


@bp.route('/clear', methods=['POST'])
def clear_history():
    """清除对话历史"""
    user_id = request.json.get('user_id', 'anonymous')
    with data_lock:
        if user_id in conversation_data:
            conversation_data[user_id]['history'] = []
    return jsonify({
        "code": 200,
        "message": "对话历史已清除"
    })


@bp.route('/status', methods=['GET'])
def check_status():
    """检查AI处理状态，优化准确性"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            "code": 400,
            "message": "用户ID不能为空"
        }), 400

    try:
        user_data = get_conversation_data(user_id)
        return jsonify({
            "code": 200,
            "processing": user_data['processing'],
            "request_id": user_data['request_id'],
            "last_active": user_data['last_active']
        })
    except Exception as e:
        current_app.logger.error(f"状态检查错误: {str(e)}")
        return jsonify({
            "code": 500,
            "message": "状态检查失败"
        }), 500


# 定时清理不活跃会话
def start_cleanup_scheduler():
    def cleanup_task():
        while True:
            time.sleep(3600)  # 每小时清理一次
            cleanup_inactive_sessions()

    thread = threading.Thread(target=cleanup_task, daemon=True)
    thread.start()


# 启动时开始清理任务
start_cleanup_scheduler()