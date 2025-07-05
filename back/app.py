from flask import Flask, g
from flask_cors import CORS
import sqlite3
import os

def create_app():
    app = Flask(__name__)

    # 加载配置文件
    app.config.from_pyfile('config.py')

    # 数据库路径
    db_path = os.path.join(os.getcwd(), 'agriculture.db')
    app.config['DATABASE'] = db_path

    def get_db():
        """获取数据库连接"""
        if 'db' not in g:
            g.db = sqlite3.connect(
                app.config['DATABASE'],
                check_same_thread=False
            )
            g.db.row_factory = sqlite3.Row
        return g.db

    def init_db():
        """初始化数据库（创建表）"""
        with app.app_context():
            db = get_db()

            # 获取 schema.sql 文件路径
            schema_path = os.path.join(app.root_path, 'schema.sql')

            # 以 UTF-8 编码读取文件内容
            with open(schema_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())

            db.commit()
            print("✅ 数据库已初始化")

    # 在应用启动时自动初始化数据库
    init_db()

    @app.teardown_appcontext
    def close_db(exception):
        """在每次请求后关闭数据库连接"""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # 提供给蓝图使用的 db 获取方式
    app.get_db = get_db

    # 启用 CORS（跨域支持）
    CORS(app,
         resources={r"/*": {
             "origins": "http://localhost:5173",
             "supports_credentials": True,
             "allow_headers": ["Content-Type", "Authorization"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
         }})

    # 注册蓝图
    from blueprints.login import bp as login_bp
    from blueprints.register import bp as register_bp
    from blueprints.yzm import bp as yzm_bp
    from blueprints.weather import bp as weather_bp
    from blueprints.shebei import bp as shebei_bp
    from blueprints.device import bp as device_bp
    from blueprints.personnel import bp as personnel_bp
    from blueprints.aiask import bp as aiask_bp
    from blueprints.temperature import bp as temperature_bp
    from blueprints.ph_data import bp as ph_data_bp
    from blueprints.wendu import bp as wendu_bp
    from blueprints.chohai import bp as chohai_bp
    from blueprints.shi1 import bp as shi1_bp
    from blueprints.shi2 import bp as shi2_bp
    from blueprints.tem import tem_bp
    from blueprints.device_warning import bp as device_warning_bp
    from blueprints.chou1 import bp as chou1_bp
    from blueprints.chou2 import bp as chou2_bp
    from blueprints.chou3 import bp as chou3_bp
    from blueprints.liebiao import bp as liebiao_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(yzm_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(shebei_bp)
    app.register_blueprint(device_bp)
    app.register_blueprint(personnel_bp)
    app.register_blueprint(aiask_bp, url_prefix='/aiask')
    app.register_blueprint(temperature_bp)
    app.register_blueprint(ph_data_bp, url_prefix='/ph_data')
    app.register_blueprint(wendu_bp)
    app.register_blueprint(chohai_bp)
    app.register_blueprint(shi1_bp)
    app.register_blueprint(shi2_bp)
    app.register_blueprint(tem_bp, url_prefix='/api')
    app.register_blueprint(device_warning_bp)
    app.register_blueprint(chou1_bp)
    app.register_blueprint(chou2_bp)
    app.register_blueprint(chou3_bp)
    app.register_blueprint(liebiao_bp)

    with app.app_context():
        try:
            from blueprints.chou1 import load_prediction_model
            load_prediction_model()
            print("✅ 预测模型已加载")
        except Exception as e:
            print(f"❌ 加载预测模型失败: {str(e)}")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)