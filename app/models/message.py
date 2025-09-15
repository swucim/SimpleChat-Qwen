from app import db
from app import db
from datetime import datetime

class Message(db.Model):
    """消息模型"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' 或 'assistant'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, conversation_id, role, content):
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def get_conversation_messages(conversation_id, limit=None):
        """获取对话的消息列表"""
        query = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def create_message(conversation_id, role, content):
        """创建新消息"""
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.session.add(message)
        db.session.commit()
        return message
    
    def __repr__(self):
        return f'<Message {self.id}: {self.role}>'