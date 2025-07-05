from flask import Blueprint, jsonify
import sqlite3
from flask_cors import cross_origin

bp = Blueprint('shi1', __name__)

def get_db_connection():
    conn = sqlite3.connect('agriculture.db')
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/moisture', methods=['GET'])
@cross_origin()
def get_moisture_data():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # 获取最近7条记录并按日期正序排列
        cur.execute('''
            SELECT record_date as date, moisture 
            FROM (
                SELECT record_date, moisture 
                FROM soil_moisture 
                ORDER BY id DESC 
                LIMIT 7
            ) 
            ORDER BY date ASC
        ''')
        rows = cur.fetchall()
        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()