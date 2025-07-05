from flask import Blueprint, jsonify, current_app, g
import sqlite3
import datetime


bp = Blueprint('device_warning', __name__, url_prefix='/api/warning')


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def is_data_constant(data_points, threshold=0.5, time_threshold_hours=2):
    """
    检测数据是否长时间保持不变
    data_points: 数据点列表，每个元素为(timestamp, value)
    threshold: 数值变化阈值，小于此值视为不变
    time_threshold_hours: 时间阈值，单位小时（默认2小时）
    """
    if len(data_points) < 2:
        return False, None

    # 检查时间跨度是否达到阈值
    first_time = datetime.datetime.strptime(data_points[0][0], '%Y-%m-%d %H:%M:%S')
    last_time = datetime.datetime.strptime(data_points[-1][0], '%Y-%m-%d %H:%M:%S')
    time_diff = last_time - first_time

    if time_diff.total_seconds() < time_threshold_hours * 3600:
        return False, None

    # 检查数值变化是否小于阈值
    first_value = data_points[0][1]
    for time, value in data_points[1:]:
        if abs(value - first_value) > threshold:
            return False, None

    return True, first_value


def check_device_warnings():
    """检查所有设备是否有数据长时间不变的情况"""
    db = get_db()
    cursor = db.cursor()

    # 获取所有设备
    cursor.execute("SELECT id, device_name, device_code FROM device")
    devices = cursor.fetchall()

    warning_updates = []

    for device in devices:
        device_id = device['id']
        device_name = device['device_name']
        device_code = device['device_code']

        # 检查设备当前状态
        cursor.execute("SELECT status FROM device WHERE id = ?", (device_id,))
        device_status = cursor.fetchone()

        # 如果设备已经是故障状态，则跳过检测
        if device_status['status'] == 'Faulty':
            continue

        warning_type = None
        warning_value = None

        # 检查温度数据（使用2小时阈值）
        cursor.execute(
            """SELECT timestamp, temperature FROM temperature_data 
               WHERE device_id = ? 
               ORDER BY timestamp DESC 
               LIMIT 24""",  # 取最近24条数据
            (device_id,)
        )
        temp_data = cursor.fetchall()

        if temp_data:
            is_constant, value = is_data_constant(
                [(item['timestamp'], item['temperature']) for item in temp_data]
            )
            if is_constant:
                warning_type = 'temperature_constant'
                warning_value = value

        # 如果温度没有问题，检查湿度数据（使用2小时阈值）
        if not warning_type:
            cursor.execute(
                """SELECT timestamp, humidity FROM temperature_data 
                   WHERE device_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT 24""",
                (device_id,)
            )
            humidity_data = cursor.fetchall()

            if humidity_data:
                is_constant, value = is_data_constant(
                    [(item['timestamp'], item['humidity']) for item in humidity_data]
                )
                if is_constant:
                    warning_type = 'humidity_constant'
                    warning_value = value

        # 如果温度和湿度都没有问题，检查pH值数据（使用1小时阈值）
        if not warning_type:
            cursor.execute(
                """SELECT timestamp, ph FROM temperature_data 
                   WHERE device_id = ? 
                   ORDER BY timestamp DESC 
                   LIMIT 24""",
                (device_id,)
            )
            ph_data = cursor.fetchall()

            if ph_data:
                is_constant, value = is_data_constant(
                    [(item['timestamp'], item['ph']) for item in ph_data],
                    threshold=0.2,  # pH变化阈值更小
                    time_threshold_hours=1  # pH检查时间阈值更短
                )
                if is_constant:
                    warning_type = 'ph_constant'
                    warning_value = value

        # 更新设备状态
        if warning_type:
            # 如果设备之前不是警告状态，则更新
            if device_status['status'] != 'Faulty':
                warning_updates.append({
                    'device_id': device_id,
                    'status': 'warning',
                    'warning_type': warning_type,
                    'warning_value': warning_value,
                    'warning_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
        else:
            # 如果设备之前是警告状态，但现在不是了，则恢复为正常状态
            if device_status['status'] == 'warning':
                warning_updates.append({
                    'device_id': device_id,
                    'status': 'normal',
                    'warning_type': None,
                    'warning_value': None,
                    'warning_time': None
                })

    # 批量更新设备状态
    for update in warning_updates:
        cursor.execute(
            """
            UPDATE device 
            SET status = ?, 
                warning_type = ?, 
                warning_value = ?, 
                warning_time = ? 
            WHERE id = ?
            """,
            (
                update['status'],
                update['warning_type'],
                update['warning_value'],
                update['warning_time'],
                update['device_id']
            )
        )

    db.commit()
    return warning_updates


@bp.route('/check', methods=['GET'])
def check_warnings():
    """检查并更新设备警告状态"""
    try:
        updates = check_device_warnings()
        return jsonify({
            'status': 'success',
            'data': updates,
            'message': f'更新了{len(updates)}个设备状态'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'检查设备警告失败: {str(e)}'
        }), 500


@bp.route('/list', methods=['GET'])
def get_warning_list():
    """获取警告设备列表（优先使用存储的故障描述）"""
    try:
        db = get_db()
        cursor = db.cursor()

        # 尝试获取完整警告信息（包括fault_description字段）
        try:
            cursor.execute(
                """
                SELECT 
                    id, 
                    device_name, 
                    device_code, 
                    status, 
                    warning_type, 
                    warning_value, 
                    warning_time,
                    fault_description  # 显式查询存储的故障描述
                FROM device 
                WHERE status = 'Faulty' OR status = 'warning'
                ORDER BY warning_time DESC
                """
            )
            warnings = cursor.fetchall()

            warning_list = []
            for warning in warnings:
                warning_dict = dict(warning)

                # 优先使用数据库中存储的fault_description
                stored_description = warning_dict.get('fault_description')

                if stored_description:
                    warning_dict['fault_description'] = stored_description
                else:
                    # 如果没有存储描述，则根据warning_type生成默认描述
                    warning_type = warning_dict.get('warning_type')
                    if warning_type == 'temperature_constant':
                        warning_dict['fault_description'] = '温度持续异常'
                    elif warning_type == 'humidity_constant':
                        warning_dict['fault_description'] = '湿度持续异常'
                    elif warning_type == 'ph_constant':
                        warning_dict['fault_description'] = 'pH值持续异常'
                    else:
                        warning_dict['fault_description'] = '环境数据异常'

                warning_list.append(warning_dict)

            return jsonify({
                'status': 'success',
                'data': warning_list,
                'message': f'获取到{len(warning_list)}个警告设备'
            })

        except sqlite3.OperationalError as e:
            # 如果表结构不完整（缺少fault_description等字段），回退到简单查询
            cursor.execute(
                """
                SELECT 
                    id, 
                    device_name, 
                    device_code, 
                    status
                FROM device 
                WHERE status = 'Faulty' OR status = 'warning'
                ORDER BY created_at DESC
                """
            )
            warnings = cursor.fetchall()

            # 简单查询结果只能提供默认描述
            warning_list = [dict(warning, fault_description='环境数据异常')
                            for warning in warnings]

            return jsonify({
                'status': 'success',
                'data': warning_list,
                'message': f'获取到{len(warning_list)}个警告设备（简化模式）'
            })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取警告设备列表失败: {str(e)}'
        }), 500

@bp.route('/resolve/<int:device_id>', methods=['POST'])
def resolve_warning(device_id):
    """解决设备警告"""
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            UPDATE device 
            SET status = 'Online', 
                warning_type = NULL, 
                warning_value = NULL, 
                warning_time = NULL 
            WHERE id = ?
            """,
            (device_id,)
        )
        db.commit()

        return jsonify({
            'status': 'success',
            'message': '设备警告已解除'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'解除设备警告失败: {str(e)}'
        }), 500


# 初始化数据库表结构（如需在代码中初始化）
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))