from app import db
from app.models import User, Conversation, Message
from flask import current_app
from datetime import datetime, timedelta

class UserService:
    """用户服务类，处理用户相关的业务逻辑"""
    
    @staticmethod
    def get_all_users(page=1, per_page=20):
        """获取所有用户列表（分页）"""
        users = User.query.order_by(User.last_active.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return users
    
    @staticmethod
    def get_user_stats():
        """获取用户统计信息"""
        total_users = User.query.count()
        admin_users = User.query.filter_by(is_admin=True).count()
        regular_users = total_users - admin_users
        
        # 活跃用户（最近7天）
        week_ago = datetime.utcnow() - timedelta(days=7)
        active_users = User.query.filter(User.last_active >= week_ago).count()
        
        return {
            'total_users': total_users,
            'admin_users': admin_users,
            'regular_users': regular_users,
            'active_users': active_users
        }
    
    @staticmethod
    def get_conversation_stats():
        """获取对话统计信息"""
        total_conversations = Conversation.query.count()
        total_messages = Message.query.count()
        
        # 今天的对话数
        today = datetime.utcnow().date()
        today_conversations = Conversation.query.filter(
            Conversation.created_at >= today
        ).count()
        
        # 今天的消息数
        today_messages = Message.query.filter(
            Message.created_at >= today
        ).count()
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'today_conversations': today_conversations,
            'today_messages': today_messages
        }
    
    @staticmethod
    def get_user_conversations(user_id, page=1, per_page=20):
        """获取指定用户的对话列表（分页）"""
        conversations = Conversation.query.filter_by(user_id=user_id)\
            .order_by(Conversation.updated_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return conversations
    
    @staticmethod
    def get_all_conversations(page=1, per_page=20):
        """获取所有对话列表（分页）"""
        conversations = Conversation.query\
            .join(User)\
            .order_by(Conversation.updated_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        return conversations
    
    @staticmethod
    def delete_user(user_id):
        """删除用户（管理员功能）"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        if user.is_admin:
            # 不允许删除管理员账号
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
    
    @staticmethod
    def authenticate_admin(username, password):
        """管理员身份验证"""
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user and user.check_password(password):
            user.update_last_active()
            return user
        return None
    
    @staticmethod
    def get_recent_activities(limit=10):
        """获取最近活动"""
        # 最近的对话
        recent_conversations = Conversation.query\
            .join(User)\
            .order_by(Conversation.created_at.desc())\
            .limit(limit).all()
        
        activities = []
        for conv in recent_conversations:
            activities.append({
                'type': 'conversation',
                'user': conv.user.username or f'用户_{conv.user.session_id[:8]}',
                'title': conv.title,
                'time': conv.created_at,
                'conversation_id': conv.id
            })
        
        return sorted(activities, key=lambda x: x['time'], reverse=True)[:limit]