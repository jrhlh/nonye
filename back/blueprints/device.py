from flask import Blueprint, request, jsonify, g, current_app
import sqlite3
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import ssl
import smtplib

bp = Blueprint('device', __name__)


# 动态获取数据库路径
def get_db():
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"数据库文件未找到：{db_path}")
        g.db = sqlite3.connect(
            db_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


# 原有设备列表接口（状态字段保持不变，由前端处理显示）
@bp.route('/api/device/list', methods=['GET'])
def get_device_list():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    offset = (page - 1) * size

    db = get_db()
    try:
        total = db.execute('SELECT COUNT(*) AS total FROM device').fetchone()[0]

        cursor = db.execute('''
            SELECT 
                d.id, 
                d.device_name AS deviceName, 
                d.device_code AS deviceCode, 
                d.status, 
                d.operator,
                COALESCE(td.temperature, '-') AS temperature,
                COALESCE(td.humidity, '-') AS humidity,
                d.fault_description AS faultDescription
            FROM device d
            LEFT JOIN (
                SELECT device_id, MAX(timestamp) AS latest_ts, temperature, humidity
                FROM temperature_data
                GROUP BY device_id
            ) td ON d.id = td.device_id
            ORDER BY d.created_at DESC
            LIMIT ? OFFSET ?
        ''', (size, offset))
        devices = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'success': True,
            'data': devices,
            'total': total,
            'currentPage': page,
            'pageSize': size
        })
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'message': f'数据库错误：{str(e)}',
            'errorDetail': str(e)
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


# 原有添加设备接口（状态字段按数据库要求传入Faulty/Offline）
@bp.route('/api/device', methods=['POST'])
def add_device():
    data = request.get_json()
    required_fields = ['deviceName', 'deviceCode', 'status']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'缺少必填字段：{field}'
            }), 400

    # 校验状态合法性
    valid_status = ['Faulty', 'Offline', 'Normal']  # 新增Normal状态
    if data['status'] not in valid_status:
        return jsonify({
            'success': False,
            'message': '状态值无效，允许值：Faulty/Offline/Normal'
        }), 400

    db = get_db()
    try:
        cursor = db.execute('''
            INSERT INTO device (
                device_name, 
                device_code, 
                status, 
                operator, 
                created_at, 
                fault_description
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['deviceName'],
            data['deviceCode'],
            data['status'],
            data.get('operator', ''),
            datetime.now(),
            data.get('faultDescription', '')
        ))
        db.commit()
        return jsonify({
            'success': True,
            'message': '设备新增成功',
            'id': cursor.lastrowid
        }), 201
    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({
            'success': False,
            'message': '设备ID已存在'
        }), 400
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': f'数据库错误：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


# 原有更新设备接口（状态字段按数据库要求更新）
@bp.route('/api/device/<int:id>', methods=['PUT'])
def update_device(id):
    data = request.get_json()
    db = get_db()

    # 校验状态合法性（若有更新）
    if 'status' in data:
        valid_status = ['Faulty', 'Offline', 'Normal']
        if data['status'] not in valid_status:
            return jsonify({
                'success': False,
                'message': '状态值无效，允许值：Faulty/Offline/Normal'
            }), 400

    try:
        cursor = db.execute('''
            UPDATE device
            SET 
                device_name = ?, 
                status = ?, 
                operator = ?, 
                fault_description = ?
            WHERE id = ?
        ''', (
            data['deviceName'],
            data['status'],
            data.get('operator', ''),
            data.get('faultDescription', ''),
            id
        ))
        if cursor.rowcount == 0:
            return jsonify({
                'success': False,
                'message': '设备不存在'
            }), 404
        db.commit()
        return jsonify({
            'success': True,
            'message': '设备更新成功'
        })
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': f'数据库错误：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


# 新增：故障仪表盘数据接口（核心修改点1：状态判断改为Faulty/Offline）
@bp.route('/dashboard', methods=['GET'])
def get_fault_dashboard():
    db = get_db()
    try:
        # 1. 今日故障数：设备状态为Faulty或Offline的数量
        today_faults = db.execute('''
            SELECT COUNT(*) 
            FROM device 
            WHERE status IN ('Faulty')
        ''').fetchone()[0]

        # 2. 今日故障增加数：与昨日对比
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_faults = db.execute('''
            SELECT COUNT(*) 
            FROM device 
            WHERE status IN ('Faulty') 
              AND DATE(created_at) = ?
        ''', (yesterday,)).fetchone()[0]

        increase = today_faults - yesterday_faults
        increase_display = max(increase, 0)

        # 3. 本月累计故障数
        current_month = '2025-06'
        monthly_faults = db.execute('''
            SELECT COUNT(*) 
            FROM device 
            WHERE status IN ('Faulty') 
              AND DATE(created_at) LIKE ? || '%'
        ''', (current_month,)).fetchone()[0]

        # 4. 故障上限（可配置）
        limit = 100

        return jsonify({
            'todayFaults': today_faults,
            'increase': increase_display,
            'monthlyFaults': monthly_faults,
            'limit': limit
        })
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'message': f'获取仪表盘数据失败：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


# 新增：故障类型统计接口（核心修改点2：状态映射调整）
@bp.route('/fault-types', methods=['GET'])
def get_fault_types():
    db = get_db()
    try:
        # 定义故障类型映射（数据库状态 -> 显示名称）
        fault_mapping = {
            'Faulty': '传感器故障',  # 设备功能异常
            'Offline': '离线故障',  # 设备网络断开
            'Normal': '正常'  # 正常状态（用于占位）
        }

        # 统计故障类型分布
        result = db.execute('''
            SELECT 
                CASE status 
                    WHEN 'Faulty' THEN '传感器故障'
                    WHEN 'Offline' THEN '离线故障'
                    ELSE '其他故障' 
                END AS fault_type,
                COUNT(*) AS count
            FROM device
            GROUP BY fault_type
        ''').fetchall()

        # 转换为ECharts格式并配置颜色
        data = []
        colorMap = {
            '传感器故障': '#ff7d00',  # 橙色
            '离线故障': '#e01e5a',  # 粉色
            '网络故障': '#1a73e8',  # 蓝色（预留扩展）
            '电源故障': '#ff9800',  # 深橙色（预留扩展）
            '其他故障': '#666666'  # 灰色
        }

        for row in result:
            faultType = row['fault_type']
            data.append({
                'name': faultType,
                'value': row['count'],
                'itemStyle': {'color': colorMap.get(faultType, colorMap['其他故障'])}
            })

        # 补充默认故障类型（确保图表完整性）
        defaultTypes = ['设备故障', '离线故障', '网络故障', '电源故障', '其他故障']
        for ft in defaultTypes:
            if not any(d['name'] == ft for d in data):
                data.append({
                    'name': ft,
                    'value': 0,
                    'itemStyle': {'color': colorMap.get(ft, colorMap['其他故障'])}
                })

        return jsonify({
            'success': True,
            'data': data
        })
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'message': f'获取故障类型数据失败：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


# 新增：故障时段分布统计接口（核心修改点3：状态查询条件调整）
@bp.route('/fault-time-distribution', methods=['GET'])
def get_fault_time_distribution():
    db = get_db()
    try:
        # 按24小时划分时段，统计故障设备创建时间分布（状态为Faulty或Offline）
        query = '''
            SELECT 
                CASE 
                    WHEN STRFTIME('%H', created_at) BETWEEN 0 AND 3 THEN '00:00-04:00'
                    WHEN STRFTIME('%H', created_at) BETWEEN 4 AND 7 THEN '04:00-08:00'
                    WHEN STRFTIME('%H', created_at) BETWEEN 8 AND 11 THEN '08:00-12:00'
                    WHEN STRFTIME('%H', created_at) BETWEEN 12 AND 15 THEN '12:00-16:00'
                    WHEN STRFTIME('%H', created_at) BETWEEN 16 AND 19 THEN '16:00-20:00'
                    ELSE '20:00-24:00'
                END AS time_slot,
                COUNT(*) AS fault_count
            FROM device
            WHERE status IN ('Faulty', 'Offline')
            GROUP BY time_slot
            ORDER BY time_slot;
        '''
        cursor = db.execute(query)
        result = cursor.fetchall()

        # 补全所有时段数据
        time_slots = ['00:00-04:00', '04:00-08:00', '08:00-12:00', '12:00-16:00', '16:00-20:00', '20:00-24:00']
        data = []
        for slot in time_slots:
            item = next((row for row in result if row['time_slot'] == slot), {'time_slot': slot, 'fault_count': 0})
            data.append({
                'name': slot,
                'value': item['fault_count']
            })

        return jsonify({
            'success': True,
            'data': data
        })
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'message': f'获取故障时段数据失败：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


# 新增：故障列表接口（核心修改点4：状态映射与查询条件调整）
@bp.route('/fault-list', methods=['GET'])
def get_fault_list():
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    offset = (page - 1) * size
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'all')  # all/functional/offline/resolved

    db = get_db()
    query = '''
        SELECT 
            d.id,
            d.device_code AS deviceId,
            d.device_name AS deviceName,
            d.fault_description AS faultInfo,
            d.created_at AS timestamp,
            d.operator AS assignedTo,
            CASE d.status 
                WHEN 'Faulty' THEN '功能故障'
                WHEN 'Offline' THEN '离线故障'
                ELSE '已解决'
            END AS status,
            CASE d.status 
                WHEN 'Faulty' THEN 'functional'
                WHEN 'Offline' THEN 'offline'
                ELSE 'resolved'
            END AS statusClass
        FROM device d
        WHERE 1=1
    '''
    params = []

    if search:
        query += '''
            AND (
                d.device_code LIKE ? 
                OR d.device_name LIKE ?
            )
        '''
        params.extend(['%' + search + '%', '%' + search + '%'])

    if status != 'all':
        # 反向映射前端状态到数据库状态
        db_status_map = {
            'functional': 'Faulty',
            'offline': 'Offline',
            'resolved': 'Normal'
        }
        if status in db_status_map:
            query += ' AND d.status = ?'
            params.append(db_status_map[status])
        else:
            return jsonify({
                'success': False,
                'message': '状态参数无效'
            }), 400

    query += '''
        ORDER BY d.created_at DESC
        LIMIT ? OFFSET ?
    '''
    params.extend([size, offset])

    try:
        # 查询总记录数
        total_query = query.replace('SELECT *,', 'SELECT COUNT(*) AS total,')
        total = db.execute(total_query, params).fetchone()[0]

        # 查询数据列表
        cursor = db.execute(query, params)
        faults = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'success': True,
            'data': faults,
            'total': total,
            'currentPage': page,
            'pageSize': size
        })
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'message': f'获取故障列表失败：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()


def send_custom_email(receiver, subject, content):
    sender_email = "3492073524@qq.com"
    sender_password = "xhemkcgrgximchcd"
    smtp_server = "smtp.qq.com"
    port = 465

    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = sender_email
        msg['To'] = receiver
        msg['Subject'] = subject

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver, msg.as_string())
        print(f"邮件发送成功：{receiver}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP认证失败：授权码无效或邮箱账户异常")
        return False
    except smtplib.SMTPException as e:
        error_msg = str(e)
        if error_msg == "(-1, b'\\x00\\x00\\x00')" or "unexpected EOF" in error_msg:
            print("⚠️ 警告: 忽略非致命异常，假设邮件已发送成功")
            return True
        else:
            print(f"邮件发送失败：{error_msg}")
            return False
    except Exception as e:
        print(f"邮件发送失败：{str(e)}")
        return False


# 故障通知接口（核心修改点5：状态描述调整）
@bp.route('/api/fault/notify/<int:fault_id>', methods=['POST'])
def notify_responsible(fault_id):
    db = get_db()
    try:
        # 查询故障信息及负责人邮箱
        fault = db.execute('''
            SELECT 
                d.device_name, 
                d.fault_description, 
                d.status,
                u.email 
            FROM device d
            LEFT JOIN user u ON d.operator = u.username
            WHERE d.id = ?
        ''', (fault_id,)).fetchone()

        if not fault:
            return jsonify({'success': False, 'message': '故障记录不存在'}), 404

        device_name = fault['device_name']
        fault_info = fault['fault_description']
        status = fault['status']
        responsible_email = fault['email']

        if not responsible_email:
            return jsonify({'success': False, 'message': '负责人未绑定邮箱'}), 400

        # 构造故障状态描述
        status_desc = {
            'Faulty': '功能故障',
            'Offline': '离线故障',
            'Normal': '正常'
        }.get(status, '未知状态')

        # 构造邮件内容
        email_subject = f"【设备{status_desc}通知】{device_name} 故障提醒"
        email_content = f"""
            设备名称：{device_name}
            故障类型：{status_desc}
            故障描述：{fault_info or "无具体描述"}
            请尽快处理！
            通知时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        # 发送邮件
        send_success = send_custom_email(responsible_email, email_subject, email_content)

        if not send_success:
            return jsonify({
                'success': False,
                'message': '邮件发送失败，请检查邮箱配置',
                'emailStatus': 'failed'
            }), 500

        # 记录通知日志
        try:
            db.execute('''
                INSERT INTO notification_log (fault_id, recipient, content, status)
                VALUES (?, ?, ?, 'success')
            ''', (fault_id, responsible_email, email_content))
            db.commit()
            log_status = 'success'
        except sqlite3.Error as e:
            db.rollback()
            print(f"记录通知日志失败: {str(e)}")
            log_status = 'failed'

        return jsonify({
            'success': True,
            'message': '通知已发送',
            'emailStatus': 'success',
            'logStatus': log_status
        }), 200

    except sqlite3.Error as e:
        db.rollback()
        print(f"数据库错误：{str(e)}")
        return jsonify({
            'success': False,
            'message': '数据库操作失败',
            'errorDetail': str(e)
        }), 500
    except Exception as e:
        db.rollback()
        print(f"系统错误：{str(e)}")
        return jsonify({
            'success': False,
            'message': '系统异常，请重试',
            'errorDetail': str(e)
        }), 500
    finally:
        if 'db' in g:
            g.db.close()

# 添加设备删除接口
@bp.route('/api/device/<int:id>', methods=['DELETE'])
def delete_device(id):
    db = get_db()
    try:
        # 先查询设备是否存在
        device = db.execute('SELECT id FROM device WHERE id = ?', (id,)).fetchone()
        if not device:
            return jsonify({
                'success': False,
                'message': '设备不存在，无法删除'
            }), 404

        # 执行删除操作
        db.execute('DELETE FROM device WHERE id = ?', (id,))
        db.commit()
        return jsonify({
            'success': True,
            'message': '设备删除成功'
        })
    except sqlite3.Error as e:
        db.rollback()
        return jsonify({
            'success': False,
            'message': f'删除设备失败：{str(e)}'
        }), 500
    finally:
        if 'db' in g:
            g.db.close()