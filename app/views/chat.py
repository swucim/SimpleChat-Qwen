from flask import Blueprint, request, jsonify, session
from flask import Blueprint, request, jsonify, session
from app.services import ChatService
from app.models import Conversation, Message
import logging

chat = Blueprint('chat', __name__)

@chat.route('/conversations')
def get_conversations():
    """获取用户的对话列表"""
    try:
        logging.info("开始获取对话列表")
        user = ChatService.get_or_create_user()
        logging.info(f"用户获取成功: {user.id}")
        
        conversations = ChatService.get_user_conversations(user.id)
        logging.info(f"找到 {len(conversations)} 个对话")
        
        conversations_data = []
        for conv in conversations:
            conversations_data.append(conv.to_dict())
        
        return jsonify({
            'success': True,
            'conversations': conversations_data
        })
    except Exception as e:
        logging.error(f"获取对话列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'获取对话列表失败: {str(e)}'
        }), 500

@chat.route('/new', methods=['POST'])
def create_conversation():
    """创建新对话"""
    try:
        user = ChatService.get_or_create_user()
        conversation = ChatService.create_conversation(user.id)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation.id,
            'message': '新对话创建成功'
        })
    except Exception as e:
        logging.error(f"创建对话失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建对话失败'
        }), 500

@chat.route('/messages/<int:conversation_id>')
def get_messages(conversation_id):
    """获取对话的消息列表"""
    try:
        user = ChatService.get_or_create_user()
        
        # 获取对话详情
        conversation_detail = ChatService.get_conversation_detail(conversation_id, user.id)
        
        if not conversation_detail:
            return jsonify({
                'success': False,
                'error': '对话不存在或无权限访问'
            }), 404
        
        return jsonify({
            'success': True,
            'conversation': conversation_detail['conversation'],
            'messages': conversation_detail['messages']
        })
    except Exception as e:
        logging.error(f"获取消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取消息失败'
        }), 500

@chat.route('/send', methods=['POST'])
def send_message():
    """发送消息"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data or 'conversation_id' not in data:
            return jsonify({
                'success': False,
                'error': '请求参数不完整'
            }), 400
        
        conversation_id = data['conversation_id']
        message = data['message'].strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400
        
        user = ChatService.get_or_create_user()
        
        # 发送消息并获取AI回复
        result = ChatService.send_message(conversation_id, message, user.id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logging.error(f"发送消息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '发送消息失败'
        }), 500

@chat.route('/delete/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """删除对话"""
    try:
        user = ChatService.get_or_create_user()
        
        if ChatService.delete_conversation(conversation_id, user.id):
            return jsonify({
                'success': True,
                'message': '对话删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '对话不存在或无权限删除'
            }), 404
            
    except Exception as e:
        logging.error(f"删除对话失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除对话失败'
        }), 500