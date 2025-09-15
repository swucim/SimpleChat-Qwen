from app import db
from app import db
from datetime import datetime

class Conversation(db.Model):
    """对话模型"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False, default='新对话')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', 
                              cascade='all, delete-orphan', order_by='Message.created_at')
    
    def __init__(self, user_id, title='新对话'):
        self.user_id = user_id
        self.title = title
    
    def update_title_from_first_message(self):
        """根据第一条消息自动生成标题"""
        first_message = self.messages.filter_by(role='user').first()
        if first_message and len(first_message.content) > 0:
            # 取前30个字符作为标题
            self.title = first_message.content[:30] + ('...' if len(first_message.content) > 30 else '')
            self.updated_at = datetime.utcnow()
            db.session.commit()
    
    def get_message_count(self):
        """获取消息数量"""
        return self.messages.count()
    
    def get_last_message_time(self):
        """获取最后一条消息时间"""
        # 直接使用关系查询，防止循环导入问题
        messages = self.messages.all()
        if messages:
            return max(msg.created_at for msg in messages)
        else:
            return self.created_at
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'message_count': self.get_message_count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_message_time': self.get_last_message_time().isoformat()
        }
    
    def __repr__(self):
        return f'<Conversation {self.id}: {self.title}>'