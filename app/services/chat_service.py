from app import db
from app import db
from app.models import User, Conversation, Message
from app.services.api_service import api_service
from flask import session, current_app
import uuid
import json
from datetime import datetime

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
            current_app.logger.info("开始调用API")
            response = api_service.send_chat_request(api_messages)
            current_app.logger.info(f"API调用完成，响应类型: {type(response)}")
            
            # 提取AI回复内容
            if 'choices' in response and len(response['choices']) > 0:
                ai_message = response['choices'][0]['message']['content']
                current_app.logger.info(f"AI回复内容长度: {len(ai_message)}")
            else:
                current_app.logger.error(f"API返回格式错误: {response}")
                raise Exception("API返回格式错误")
            
            # 保存AI回复
            current_app.logger.info("开始保存AI回复")
            ai_msg = Message.create_message(conversation_id, 'assistant', ai_message)
            current_app.logger.info(f"AI消息保存成功，ID: {ai_msg.id}")
            
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
    
    @staticmethod
    def send_message_stream(conversation_id, user_message, user_id=None):
        """
        发送消息并获取AI流式回复
        
        Args:
            conversation_id: 对话ID
            user_message: 用户消息内容
            user_id: 用户ID（用于验证权限）
            
        Returns:
            generator: 流式生成器
        """
        import json
        from flask import current_app
        
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
            
            # 构建 API 请求的消息格式
            api_messages = []
            for msg in messages:
                api_messages.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # 调用API获取流式回复
            stream_generator = api_service.send_chat_request(api_messages, stream=True)
            
            # 用于积累完整回复内容
            full_response = ""
            ai_msg = None  # 初始化AI消息对象
            
            # 获取应用实例
            app = current_app._get_current_object()
            
            # 生成流式数据
            def stream_with_save():
                nonlocal full_response, ai_msg
                try:
                    with app.app_context():
                        yield f"data: {json.dumps({
                            'type': 'user_message',
                            'message': user_msg.to_dict()
                        }, ensure_ascii=False)}\n\n"
                        
                        yield f"data: {json.dumps({
                            'type': 'ai_start'
                        }, ensure_ascii=False)}\n\n"
                        
                        chunk_count = 0
                        for chunk in stream_generator:
                            full_response += chunk
                            chunk_count += 1
                            yield f"data: {json.dumps({
                                'type': 'ai_chunk',
                                'content': chunk
                            }, ensure_ascii=False)}\n\n"
                            
                            # 每有50个chunk记录一次日志
                            if chunk_count % 50 == 0:
                                current_app.logger.info(f"已处理 {chunk_count} 个chunk，当前内容长度: {len(full_response)}")
                        
                        current_app.logger.info(f"流式输出完成，总共 {chunk_count} 个chunk，最终内容长度: {len(full_response)}")
                        
                        # 保存完整的AI回复
                        if full_response.strip():  # 确保有内容才保存
                            current_app.logger.info(f"保存AI回复，内容长度: {len(full_response)}")
                            ai_msg = Message.create_message(conversation_id, 'assistant', full_response)
                            current_app.logger.info(f"AI消息保存成功，ID: {ai_msg.id}")
                        else:
                            current_app.logger.warning("没有收到AI回复内容")
                            # 创建一个错误消息
                            ai_msg = Message.create_message(conversation_id, 'assistant', '回复失败，请重试')
                        
                        yield f"data: {json.dumps({
                            'type': 'ai_complete',
                            'message': ai_msg.to_dict()
                        }, ensure_ascii=False)}\n\n"
                        
                        yield "data: [DONE]\n\n"
                        
                except Exception as e:
                    # 使用标准logging，避免应用上下文问题
                    import logging
                    logging.error(f"流式处理错误: {str(e)}", exc_info=True)
                    
                    # 如果有部分内容，尝试保存
                    if full_response.strip() and ai_msg is None:
                        try:
                            with app.app_context():
                                logging.info(f"尝试保存部分内容，长度: {len(full_response)}")
                                ai_msg = Message.create_message(conversation_id, 'assistant', full_response)
                                logging.info(f"错误情况下保存部分内容成功，ID: {ai_msg.id}")
                        except Exception as save_error:
                            logging.error(f"保存部分内容失败: {str(save_error)}")
                    
                    yield f"data: {json.dumps({
                        'type': 'error',
                        'error': str(e)
                    }, ensure_ascii=False)}\n\n"
            
            return stream_with_save()
            
        except Exception as e:
            import logging
            logging.error(f"发送流式消息失败: {str(e)}")
            def error_generator():
                yield f"data: {json.dumps({
                    'type': 'error',
                    'error': str(e)
                }, ensure_ascii=False)}\n\n"
            return error_generator()