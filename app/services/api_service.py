import requests
import json
from flask import current_app
from app.models.config_model import Config

class APIService:
    """API服务类，处理与大模型的交互"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_api_config(self):
        """获取API配置"""
        # 优先从数据库获取配置，否则使用应用配置
        db_config = Config.get_openai_config()
        
        config = {
            'api_url': db_config['api_url'] or current_app.config['OPENAI_API_URL'],
            'api_key': db_config['api_key'] or current_app.config['OPENAI_API_KEY'],
            'model': db_config['model'] or current_app.config['OPENAI_MODEL']
        }
        
        return config
    
    def send_chat_request(self, messages, stream=False):
        """
        发送聊天请求到API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            stream: 是否使用流式响应
            
        Returns:
            dict: API响应结果
        """
        config = self.get_api_config()
        
        if not config['api_key']:
            raise ValueError("API密钥未配置")
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config["api_key"]}'
        }
        
        payload = {
            'model': config['model'],
            'messages': messages,
            'stream': stream,
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        try:
            response = self.session.post(
                config['api_url'],
                headers=headers,
                json=payload,
                timeout=60,  # 增加超时时间到60秒
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()
                
        except requests.exceptions.Timeout as e:
            current_app.logger.error(f"API请求超时: {str(e)}")
            raise Exception("API请求超时，请稍后重试")
        except requests.exceptions.ConnectionError as e:
            current_app.logger.error(f"API连接失败: {str(e)}")
            raise Exception("无法连接到API服务，请检查网络连接")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"API请求失败: {str(e)}")
            raise Exception(f"API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            current_app.logger.error(f"API响应解析失败: {str(e)}")
            raise Exception("API响应格式错误")
    
    def _handle_stream_response(self, response):
        """处理流式响应"""
        try:
            content = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # 移除 'data: ' 前缀
                        if data.strip() == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get('choices', [{}])[0].get('delta', {})
                            if 'content' in delta:
                                content += delta['content']
                        except json.JSONDecodeError:
                            continue
            
            return {
                'choices': [{
                    'message': {
                        'role': 'assistant',
                        'content': content
                    }
                }]
            }
        except Exception as e:
            current_app.logger.error(f"流式响应处理失败: {str(e)}")
            raise Exception(f"响应处理失败: {str(e)}")
    
    def test_connection(self, api_url=None, api_key=None, model=None):
        """
        测试API连接
        
        Args:
            api_url: API地址（可选，用于测试新配置）
            api_key: API密钥（可选，用于测试新配置）
            model: 模型名称（可选，用于测试新配置）
            
        Returns:
            dict: 测试结果
        """
        # 如果提供了参数，使用测试参数；否则使用当前配置
        if api_url or api_key or model:
            config = self.get_api_config()
            test_config = {
                'api_url': api_url or config['api_url'],
                'api_key': api_key or config['api_key'],
                'model': model or config['model']
            }
        else:
            test_config = self.get_api_config()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {test_config["api_key"]}'
        }
        
        payload = {
            'model': test_config['model'],
            'messages': [{"role": "user", "content": "Hello"}],
            'max_tokens': 10
        }
        
        try:
            response = self.session.post(
                test_config['api_url'],
                headers=headers,
                json=payload,
                timeout=30  # 测试连接保持30秒超时
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'message': 'API连接测试成功'
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'API连接测试失败: {str(e)}'
            }

# 全局API服务实例
api_service = APIService()