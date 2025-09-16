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
            dict or generator: API响应结果或流式生成器
        """
        config = self.get_api_config()
        
        if not config['api_key']:
            current_app.logger.warning("模拟流式输出：API密钥未配置")
            # 返回模拟流式生成器，传入None作为响应
            if stream:
                return self._stream_response_generator(None)
            else:
                return {
                    'choices': [{
                        'message': {
                            'role': 'assistant',
                            'content': '您好！我是AI助手，很高兴为您服务！请问有什么我可以帮助您的吗？'
                        }
                    }]
                }
        
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
                return self._stream_response_generator(response)
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
    
    def _stream_response_generator(self, response):
        """生成流式响应数据"""
        try:
            current_app.logger.info("开始处理流式响应")
            chunk_count = 0
            
            # 如果没有response，使用模拟数据
            if response is None:
                current_app.logger.warning("API密钥未配置，使用模拟数据")
                # 模拟流式输出数据用于测试
                demo_chunks = [
                    "您好！",
                    "我是",
                    "AI",
                    "助手，",
                    "很高兴",
                    "为您",
                    "服务！",
                    "请问",
                    "有什么",
                    "我可以",
                    "帮助您的吗？"
                ]
                import time
                for chunk in demo_chunks:
                    time.sleep(0.1)  # 模拟网络延迟
                    yield chunk
                return
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    current_app.logger.debug(f"收到原始行: {line}")
                    
                    if line.startswith('data: '):
                        data = line[6:]  # 移除 'data: ' 前缀
                        if data.strip() == '[DONE]':
                            current_app.logger.info("收到结束标记")
                            break
                        
                        try:
                            chunk = json.loads(data)
                            current_app.logger.debug(f"解析的chunk: {chunk}")
                            
                            # 尝试不同的响应格式
                            content = None
                            
                            # OpenAI格式
                            if 'choices' in chunk:
                                delta = chunk.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content')
                            
                            # 硅基流动格式（可能直接包含content）
                            elif 'content' in chunk:
                                content = chunk.get('content')
                            
                            # 其他可能的格式
                            elif 'text' in chunk:
                                content = chunk.get('text')
                            
                            if content:
                                chunk_count += 1
                                current_app.logger.debug(f"第{chunk_count}个chunk: {content}")
                                yield content
                            
                        except json.JSONDecodeError as e:
                            current_app.logger.warning(f"JSON解析失败: {e}, 数据: {data}")
                            continue
                            
            current_app.logger.info(f"流式响应处理完成，总共处理了 {chunk_count} 个chunk")
            
        except Exception as e:
            current_app.logger.error(f"流式响应处理失败: {str(e)}", exc_info=True)
            raise Exception(f"响应处理失败: {str(e)}")
    
    def _handle_stream_response(self, response):
        """处理流式响应（遗留用于兼容性）"""
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