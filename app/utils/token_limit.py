from functools import wraps
from flask import jsonify, request
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

        # 检查请求中是否使用自定义 API 配置
        # 如果使用自定义 API 配置，则不受服务端限额限制
        try:
            data = request.get_json() or {}
            custom_config = data.get('custom_api') or {}
            custom_api_key = custom_config.get('api_key')
            
            # 如果用户提供了自定义 API key，跳过限额检查
            if custom_api_key:
                return f(*args, **kwargs)
        except Exception:
            # 如果无法解析请求数据，继续执行限额检查
            pass

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
