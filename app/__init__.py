from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import os

# 扩展实例
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name=None):
    """应用工厂函数"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV') or 'development'
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # 配置登录管理器
    login_manager.login_view = 'admin.login'
    login_manager.login_message = '请先登录访问此页面'
    login_manager.login_message_category = 'info'
    
    # 注册蓝图
    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.views.chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint, url_prefix='/api/chat')
    
    from app.views.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    # 在应用上下文中创建数据库表
    with app.app_context():
        from app.models import user, conversation, message, config_model
        db.create_all()
        
        # 创建默认管理员账号
        from app.models.user import User
        admin_user = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if not admin_user:
            admin_user = User(
                username=app.config['ADMIN_USERNAME'],
                is_admin=True
            )
            admin_user.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin_user)
            db.session.commit()
    
    return app