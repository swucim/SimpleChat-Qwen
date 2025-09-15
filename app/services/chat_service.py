from app import db
from app import db
from app.models import User, Conversation, Message
from app.services.api_service import api_service
from flask import session, current_app
import uuid

class ChatService:
    """聊天服务类，处理对话相关的业务逻辑"""
    
    @staticmethod
    def get_or_create_user():
        """获取或创建当前用户"""
        try:
            # 从session中获取用户ID，如果没有则创建新的会话ID
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
                current_app.logger.info(f"创建新的session_id: {session['session_id']}")
            
            session_id = session['session_id']
            current_app.logger.info(f"使用session_id: {session_id}")
            
            user = User.get_or_create_by_session(session_id)
            current_app.logger.info(f"用户创建/获取成功: {user.id}")
            
            return user
        except Exception as e:
            current_app.logger.error(f"获取或创建用户失败: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def create_conversation(user_id, title='新对话'):
        """创建新对话"""
        conversation = Conversation(user_id=user_id, title=title)
        db.session.add(conversation)
        db.session.commit()
        return conversation
    
    @staticmethod
    def get_user_conversations(user_id, limit=50):
        """获取用户的对话列表"""
        conversations = Conversation.query.filter_by(user_id=user_id)\
            .order_by(Conversation.updated_at.desc())\
            .limit(limit).all()
        return conversations
    
    @staticmethod
    def get_conversation_messages(conversation_id, user_id=None):
        """获取对话的消息列表"""
        # 验证对话是否属于用户
        if user_id:
            conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
            if not conversation:
                return None
        
        messages = Message.get_conversation_messages(conversation_id)
        return messages
    
    @staticmethod
    def send_message(conversation_id, user_message, user_id=None):
        """
        发送消息并获取AI回复
        
        Args:
            conversation_id: 对话ID
            user_message: 用户消息内容
            user_id: 用户ID（用于验证权限）
            
        Returns:
            dict: 包含用户消息和AI回复的结果
        """
        try:
            # 验证对话是否属于用户
            if user_id:
                conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
                if not conversation:
                    raise ValueError("对话不存在或无权限访问")
            else:
                conversation = Conversation.query.get(conversation_id)
                if not conversation:
                    raise ValueError("对话不存在")
            
            # 保存用户消息
            user_msg = Message.create_message(conversation_id, 'user', user_message)
            
            # 如果是第一条消息，自动生成对话标题
            if conversation.get_message_count() == 1:
                conversation.update_title_from_first_message()
            
            # 获取对话历史（最近20条消息）
            messages = Message.get_conversation_messages(conversation_id, limit=20)
            
            # 构建API请求的消息格式
            api_messages = []
            for msg in messages:
                api_messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # 调用API获取回复
            response = api_service.send_chat_request(api_messages)
            
            # 提取AI回复内容
            if 'choices' in response and len(response['choices']) > 0:
                ai_message = response['choices'][0]['message']['content']
            else:
                raise Exception("API返回格式错误")
            
            # 保存AI回复
            ai_msg = Message.create_message(conversation_id, 'assistant', ai_message)
            
            return {
                'success': True,
                'user_message': user_msg.to_dict(),
                'ai_message': ai_msg.to_dict()
            }
            
        except Exception as e:
            current_app.logger.error(f"发送消息失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_conversation(conversation_id, user_id):
        """删除对话"""
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
        if not conversation:
            return False
        
        db.session.delete(conversation)
        db.session.commit()
        return True
    
    @staticmethod
    def get_conversation_detail(conversation_id, user_id=None):
        """获取对话详情"""
        if user_id:
            conversation = Conversation.query.filter_by(id=conversation_id, user_id=user_id).first()
        else:
            conversation = Conversation.query.get(conversation_id)
        
        if not conversation:
            return None
        
        messages = ChatService.get_conversation_messages(conversation_id)
        
        return {
            'conversation': conversation.to_dict(),
            'messages': [msg.to_dict() for msg in messages] if messages else []
        }