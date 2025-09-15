from app import db, login_manager
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=True, index=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, session_id=None, username=None, is_admin=False):
        if session_id:
            self.session_id = session_id
        if username:
            self.username = username
        self.is_admin = is_admin
        self.last_active = datetime.utcnow()
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_active(self):
        """更新最后活跃时间"""
        self.last_active = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_or_create_by_session(session_id):
        """根据会话ID获取或创建用户"""
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            user = User(session_id=session_id)
            db.session.add(user)
            db.session.commit()
        else:
            user.update_last_active()
        return user
    
    def __repr__(self):
        return f'<User {self.username or self.session_id}>'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 用户加载器"""
    return User.query.get(int(user_id))