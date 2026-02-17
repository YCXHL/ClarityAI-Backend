from functools import wraps
from flask import jsonify
import os


def check_token_limit(f):
    """检查 token 限额的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取限额配置
        token_limit = int(os.getenv('DAILY_TOKEN_LIMIT', '0'))
        
        # 如果限额为 0，表示无限制
        if token_limit == 0:
            return f(*args, **kwargs)
        
        # 检查今日 token 使用量
        from app.models.session import SessionManager
        today_usage = SessionManager.get_today_token_usage()
        
        if today_usage >= token_limit:
            return jsonify({
                'error': 'token_limit_reached',
                'message': '服务端已达单日 token 限额，请明日再试或切换/搭建个人服务端',
                'token_limit': token_limit,
                'today_usage': today_usage
            }), 429
        
        return f(*args, **kwargs)
    
    return decorated_function
