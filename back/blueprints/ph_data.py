from flask import Blueprint, jsonify, request, current_app, g
import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bp = Blueprint('ph_data', __name__, url_prefix='/ph_data')

# 数据缓存字典，格式: {time_range: (seed, cached_data)}
ph_data_cache = {}


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(
                current_app.config.get('DATABASE', 'agriculture.db'),
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            g.db.row_factory = sqlite3.Row
            logger.info("数据库连接成功")
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logger.info("数据库连接已关闭")


@bp.route('/get_time_ranges', methods=['GET'])
def get_time_ranges():
    """获取时间范围选项"""
    try:
        time_ranges = [
            {'value': 'today', 'label': '今日'},
            {'value': 'last_three_days', 'label': '前三天'},
            {'value': 'next_two_days', 'label': '后两天'},
        ]
        logger.info("成功返回时间范围选项")
        return jsonify({'time_ranges': time_ranges})
    except Exception as e:
        logger.error(f"获取时间范围失败: {str(e)}")
        return jsonify({'error': '获取时间范围失败'}), 500


def increase_ph_fluctuation(data_list, time_range, amplitude=1.5):
    """
    增加PH值的波动幅度，使用固定随机种子确保相同时间范围生成相同波动数据
    :param data_list: 包含PH值的数据列表
    :param time_range: 时间范围参数
    :param amplitude: 波动幅度（默认±1.5）
    :return: 修改后的列表
    """
    # 检查缓存
    if time_range in ph_data_cache:
        logger.info(f"使用缓存的波动数据 for {time_range}")
        return ph_data_cache[time_range]

    # 为特定时间范围设置固定随机种子
    seed = hash(time_range)
    random.seed(seed)
    logger.info(f"为时间范围 {time_range} 设置随机种子: {seed}")

    # 应用波动
    modified_data = []
    for item in data_list:
        original_ph = item.get('ph') or item.get('avg_ph')
        if original_ph is not None:
            # 随机波动（可正可负）
            fluctuation = random.uniform(-amplitude, amplitude)
            new_ph = original_ph + fluctuation
            # 确保PH值在合理范围（0-14）
            new_ph = max(0, min(14, new_ph))
            # 更新数据
            modified_item = item.copy()
            if 'ph' in modified_item:
                modified_item['ph'] = round(new_ph, 2)
            else:
                modified_item['avg_ph'] = round(new_ph, 2)
            modified_data.append(modified_item)

    # 缓存波动后的数据
    ph_data_cache[time_range] = modified_data
    return modified_data


@bp.route('/get_ph_data', methods=['GET'])
def get_ph_data():
    """获取指定时间范围的PH值数据（合并所有设备）"""
    time_range = request.args.get('time_range', 'today')
    sample_method = request.args.get('sample_method', 'fixed')  # 采样方式：fixed(固定点)或hourly(每小时)
    logger.info(f"请求PH数据，时间范围: {time_range}，采样方式: {sample_method}")

    if time_range not in ['today', 'last_three_days', 'next_two_days', 'all']:
        logger.warning(f"无效的时间范围: {time_range}")
        return jsonify({'error': '无效的时间范围'}), 400

    try:
        db = get_db()
        # 硬编码今日为2025-05-27
        today = datetime.datetime(2025, 5, 27)
        today_str = today.strftime('%Y-%m-%d')

        result = []

        if time_range == 'today':
            # 今日数据查询逻辑
            start_date = today_str + ' 00:00:00'
            end_date = today_str + ' 23:59:59'

            if sample_method == 'hourly':
                # 每小时采样
                for hour in range(0, 24):
                    sample_time = f"{today_str} {hour:02d}:00:00"
                    start_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                  - relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                    end_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                + relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

                    cursor = db.execute(
                        '''SELECT AVG(ph) as avg_ph 
                           FROM temperature_data 
                           WHERE (timestamp BETWEEN ? AND ?) 
                              OR (DATE(timestamp) = DATE(?))''',
                        (start_time, end_time, sample_time)
                    )
                    row = cursor.fetchone()
                    avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                    result.append({
                        'timestamp': sample_time,
                        'ph': round(avg_ph, 2)
                    })
            else:
                # 固定点采样
                cursor = db.execute(
                    '''SELECT timestamp, AVG(ph) as avg_ph 
                       FROM temperature_data 
                       WHERE (timestamp BETWEEN ? AND ?) 
                          OR (DATE(timestamp) = DATE(?))
                       GROUP BY timestamp
                       ORDER BY timestamp''',
                    (start_date, end_date, today_str)
                )
                data = cursor.fetchall()
                result = [{'timestamp': row['timestamp'], 'ph': float(row['avg_ph'])} for row in data]

            logger.info(f"查询到今日PH数据记录: {len(result)} 条")

        elif time_range == 'last_three_days':
            # 前三天数据查询
            if sample_method == 'hourly':
                # 每小时采样
                for i in range(3, 0, -1):
                    date = today - relativedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    for hour in range(0, 24):
                        sample_time = f"{date_str} {hour:02d}:00:00"
                        start_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                      - relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                        end_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                    + relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

                        cursor = db.execute(
                            '''SELECT AVG(ph) as avg_ph 
                               FROM temperature_data 
                               WHERE (timestamp BETWEEN ? AND ?) 
                                  OR (DATE(timestamp) = DATE(?))''',
                            (start_time, end_time, sample_time)
                        )
                        row = cursor.fetchone()
                        avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                        result.append({
                            'timestamp': sample_time,
                            'ph': round(avg_ph, 2)
                        })
            else:
                # 固定点采样（每天6个点）
                sample_hours = [4, 8, 12, 16, 20, 23]
                for i in range(3, 0, -1):
                    date = today - relativedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    for hour in sample_hours:
                        if hour == 23:
                            sample_time = f"{date_str} {hour:02d}:00:00"
                        else:
                            sample_time = f"{date_str} {hour:02d}:00:00"

                        start_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                      - relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                        end_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                    + relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

                        cursor = db.execute(
                            '''SELECT AVG(ph) as avg_ph 
                               FROM temperature_data 
                               WHERE (timestamp BETWEEN ? AND ?) 
                                  OR (DATE(timestamp) = DATE(?))''',
                            (start_time, end_time, sample_time)
                        )
                        row = cursor.fetchone()
                        avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                        result.append({
                            'timestamp': sample_time,
                            'ph': round(avg_ph, 2)
                        })

            logger.info(f"查询到前三天PH数据记录: {len(result)} 条")

        elif time_range == 'next_two_days':
            # 后两天数据查询
            if sample_method == 'hourly':
                for i in range(1, 3):
                    date = today + relativedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    for hour in range(0, 24):
                        sample_time = f"{date_str} {hour:02d}:00:00"
                        start_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                      - relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                        end_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                    + relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

                        cursor = db.execute(
                            '''SELECT AVG(ph) as avg_ph 
                               FROM temperature_data 
                               WHERE (timestamp BETWEEN ? AND ?) 
                                  OR (DATE(timestamp) = DATE(?))''',
                            (start_time, end_time, sample_time)
                        )
                        row = cursor.fetchone()
                        avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                        result.append({
                            'timestamp': sample_time,
                            'ph': round(avg_ph, 2)
                        })
            else:
                sample_hours = [8, 12, 16, 20]
                for i in range(1, 3):
                    date = today + relativedelta(days=i)
                    date_str = date.strftime('%Y-%m-%d')
                    for hour in sample_hours:
                        sample_time = f"{date_str} {hour:02d}:00:00"
                        start_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                      - relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                        end_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                    + relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

                        cursor = db.execute(
                            '''SELECT AVG(ph) as avg_ph 
                               FROM temperature_data 
                               WHERE (timestamp BETWEEN ? AND ?) 
                                  OR (DATE(timestamp) = DATE(?))''',
                            (start_time, end_time, sample_time)
                        )
                        row = cursor.fetchone()
                        avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                        result.append({
                            'timestamp': sample_time,
                            'ph': round(avg_ph, 2)
                        })

            logger.info(f"查询到后两天PH数据记录: {len(result)} 条")

        elif time_range == 'all':
            # 查询所有PH数据
            cursor = db.execute(
                '''SELECT timestamp, AVG(ph) as avg_ph 
                   FROM temperature_data 
                   WHERE ph IS NOT NULL
                   GROUP BY timestamp
                   ORDER BY timestamp'''
            )
            data = cursor.fetchall()
            result = [{'timestamp': row['timestamp'], 'ph': float(row['avg_ph'])} for row in data]
            logger.info(f"查询到所有PH数据记录: {len(result)} 条")

        # 关键修改：使用带随机种子的波动函数，并缓存结果
        result = increase_ph_fluctuation(result, time_range, amplitude=2.0)

        return jsonify({
            'time_range': time_range,
            'sample_method': sample_method,
            'data': result
        })

    except sqlite3.Error as e:
        logger.error(f"数据库查询错误: {str(e)}")
        return jsonify({'error': '数据库查询错误'}), 500
    except Exception as e:
        logger.error(f"获取PH数据异常: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        close_db()


@bp.route('/get_ph_data_by_date_range', methods=['GET'])
def get_ph_data_by_date_range():
    """获取指定日期范围内的PH值数据（合并所有设备）"""
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    sample_method = request.args.get('sample_method', 'daily')  # 采样方式：daily(每日)或hourly(每小时)

    # 验证日期格式
    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        logger.warning(f"无效的日期格式，需要YYYY-MM-DD格式，实际传入: {start_date_str}, {end_date_str}")
        return jsonify({'error': '无效的日期格式，需要YYYY-MM-DD格式'}), 400

    # 验证日期范围
    if start_date > end_date:
        logger.warning(f"开始日期不能大于结束日期: {start_date_str} > {end_date_str}")
        return jsonify({'error': '开始日期不能大于结束日期'}), 400

    logger.info(f"请求PH数据，日期范围: {start_date_str} 至 {end_date_str}，采样方式: {sample_method}")

    try:
        db = get_db()
        result = []

        if sample_method == 'hourly':
            # 每小时采样
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                for hour in range(0, 24):
                    sample_time = f"{date_str} {hour:02d}:00:00"
                    start_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                  - relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
                    end_time = (datetime.datetime.strptime(sample_time, '%Y-%m-%d %H:%M:%S')
                                + relativedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

                    cursor = db.execute(
                        '''SELECT AVG(ph) as avg_ph 
                           FROM temperature_data 
                           WHERE (timestamp BETWEEN ? AND ?) 
                              OR (DATE(timestamp) = DATE(?))''',
                        (start_time, end_time, sample_time)
                    )
                    row = cursor.fetchone()
                    avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                    result.append({
                        'timestamp': sample_time,
                        'ph': round(avg_ph, 2)
                    })
                current_date += relativedelta(days=1)
        else:
            # 每日采样
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                cursor = db.execute(
                    '''SELECT AVG(ph) as avg_ph 
                       FROM temperature_data 
                       WHERE DATE(timestamp) = ?''',
                    (date_str,)
                )
                row = cursor.fetchone()
                avg_ph = float(row['avg_ph']) if row and row['avg_ph'] is not None else 0

                result.append({
                    'date': date_str,
                    'avg_ph': round(avg_ph, 2)
                })
                current_date += relativedelta(days=1)

        logger.info(f"查询到{start_date_str}至{end_date_str}的PH数据记录: {len(result)} 条")

        # 增加PH值的波动幅度，使用日期范围字符串作为种子
        range_key = f"{start_date_str}_{end_date_str}"
        result = increase_ph_fluctuation(result, range_key, amplitude=2.0)

        return jsonify({
            'start_date': start_date_str,
            'end_date': end_date_str,
            'sample_method': sample_method,
            'data': result
        })

    except sqlite3.Error as e:
        logger.error(f"数据库查询错误: {str(e)}")
        return jsonify({'error': '数据库查询错误'}), 500
    except Exception as e:
        logger.error(f"获取PH数据异常: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500
    finally:
        close_db()


@bp.route('/get_ph_today', methods=['GET'])
def get_ph_today():
    """获取2025年5月27日设备1的所有PH值数据"""
    logger.info("请求获取2025年5月27日设备1的PH数据")
    try:
        db = get_db()
        target_date = datetime.datetime(2025, 5, 27)
        start = target_date.strftime('%Y-%m-%d 00:00:00')
        end = target_date.strftime('%Y-%m-%d 23:59:59')

        logger.info(f"查询范围: {start} ~ {end}，设备ID: 1")
        cursor = db.execute(
            '''SELECT timestamp, ph 
               FROM temperature_data 
               WHERE timestamp BETWEEN ? AND ? 
               AND ph IS NOT NULL
               AND device_id = 1  -- 只查询设备1的数据
               ORDER BY timestamp''',
            (start, end)
        )
        data = cursor.fetchall()

        if not data:
            logger.warning("2025-05-27设备1无PH数据，查询最近10条调试")
            debug_cursor = db.execute('''
                SELECT timestamp, ph, device_id
                FROM temperature_data 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            recent = debug_cursor.fetchall()
            logger.info("数据库最近10条记录:")
            for record in recent:
                logger.info(f"  timestamp: {record['timestamp']}, ph: {record['ph']}, device_id: {record['device_id']}")
            return jsonify({
                'date': '2025-05-27',
                'device_id': 1,
                'message': '未找到设备1的PH数据',
                'data': []
            })

        result = []
        for i, row in enumerate(data):
            try:
                # 提取原始数据
                raw_ts = row['timestamp']
                raw_ph = row['ph']

                # 验证时间格式
                if isinstance(raw_ts, datetime.datetime):
                    dt = raw_ts
                else:
                    dt = datetime.datetime.strptime(raw_ts, '%Y-%m-%d %H:%M:%S')

                # 验证PH值
                if raw_ph is None:
                    continue  # 跳过空值

                if isinstance(raw_ph, (float, int)):
                    ph_value = raw_ph
                elif isinstance(raw_ph, str):
                    ph_str = raw_ph.strip()
                    if 'pH' in ph_str:
                        ph_str = ph_str.replace('pH', '').strip()
                    ph_value = float(ph_str)
                else:
                    ph_value = float(raw_ph)

                result.append({
                    'timestamp': raw_ts.strftime('%Y-%m-%d %H:%M:%S') if isinstance(raw_ts,
                                                                                    datetime.datetime) else raw_ts,
                    'ph': round(ph_value, 2),
                    'formatted_time': dt.strftime('%H:%M')
                })
            except ValueError as ve:
                logger.error(f"第 {i + 1} 条记录格式错误: {str(ve)}")
                logger.error(f"  原始数据: timestamp={raw_ts}, ph={raw_ph}")
            except TypeError as te:
                logger.error(f"第 {i + 1} 条记录类型错误: {str(te)}")
                logger.error(f"  原始数据: timestamp={raw_ts}, ph={raw_ph}")
            except Exception as e:
                logger.error(f"处理第 {i + 1} 条记录时未知错误: {str(e)}")

        if not result:
            logger.warning("设备1的所有记录处理后无有效数据")
            return jsonify({
                'date': '2025-05-27',
                'device_id': 1,
                'message': '数据格式错误，无有效PH值',
                'data': []
            })

        logger.info(f"成功处理设备1的 {len(result)} 条有效数据")
        return jsonify({
            'date': '2025-05-27',
            'device_id': 1,
            'total_records': len(result),
            'data': result
        })

    except sqlite3.OperationalError as oe:
        logger.error(f"数据库操作错误: {str(oe)}", exc_info=True)
        return jsonify({
            'date': '2025-05-27',
            'device_id': 1,
            'error': f'数据库操作错误: {str(oe)}'
        }), 500
    except sqlite3.Error as se:
        logger.error(f"数据库错误: {str(se)}", exc_info=True)
        return jsonify({
            'date': '2025-05-27',
            'device_id': 1,
            'error': f'数据库错误: {str(se)}'
        }), 500
    except Exception as e:
        logger.error(f"未知异常: {str(e)}", exc_info=True)
        return jsonify({
            'date': '2025-05-27',
            'device_id': 1,
            'error': f'未知错误: {str(e)}'
        }), 500
    finally:
        close_db()