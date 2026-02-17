from flask import Flask
from flask_cors import CORS
import os
from app.models.session import SessionManager


def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # 启用CORS
    CORS(app)
    
    # 初始化数据库
    SessionManager.init_db()
    SessionManager.init_token_usage()

    # 注册蓝图
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app