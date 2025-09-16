from flask import Blueprint, request, jsonify, session, Response
from flask import Blueprint, request, jsonify, session, Response
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
    """发送消息（备用非流式端点）"""
    try:
        logging.info("收到发送消息请求")
        data = request.get_json()
        logging.info(f"请求数据: {data}")
        
        if not data or 'message' not in data or 'conversation_id' not in data:
            logging.error("请求参数不完整")
            return jsonify({
                'success': False,
                'error': '请求参数不完整'
            }), 400
        
        conversation_id = data['conversation_id']
        message = data['message'].strip()
        
        if not message:
            logging.error("消息内容为空")
            return jsonify({
                'success': False,
                'error': '消息内容不能为空'
            }), 400
        
        logging.info(f"处理消息: conversation_id={conversation_id}, message='{message[:50]}...'")
        
        user = ChatService.get_or_create_user()
        logging.info(f"用户ID: {user.id}")
        
        # 使用原有的非流式方法确保保存
        logging.info("开始调用ChatService.send_message")
        result = ChatService.send_message(conversation_id, message, user.id)
        logging.info(f"ChatService.send_message返回结果: {result.get('success', False)}")
        
        if result['success']:
            logging.info("消息发送成功，返回结果")
            return jsonify(result)
        else:
            logging.error(f"消息发送失败: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logging.error(f"发送消息异常: {str(e)}", exc_info=True)
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

@chat.route('/send-stream', methods=['POST'])
def send_message_stream():
    """发送消息（流式响应）"""
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
        
        # 获取流式生成器
        stream_generator = ChatService.send_message_stream(conversation_id, message, user.id)
        
        def generate_with_logging():
            """包装生成器以添加日志"""
            logging.info(f"开始流式响应: conversation_id={conversation_id}, message_len={len(message)}")
            chunk_count = 0
            try:
                for chunk in stream_generator:
                    chunk_count += 1
                    if chunk_count % 10 == 0:  # 每10个chunk记录一次
                        logging.info(f"已发送 {chunk_count} 个chunk")
                    yield chunk
                logging.info(f"流式响应完成: 总共发送 {chunk_count} 个chunk")
            except Exception as e:
                logging.error(f"流式生成器错误: {str(e)}", exc_info=True)
                raise
        
        return Response(
            generate_with_logging(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )
            
    except Exception as e:
        logging.error(f"发送流式消息失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': '发送消息失败'
        }), 500