import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API 配置
    OPENAI_API_URL = os.environ.get('OPENAI_API_URL') or 'https://api.siliconflow.cn/v1/chat/completions'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ''
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'Qwen/Qwen2-7B-Instruct'
    
    # 管理员配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    
    # 端口配置
    DEV_PORT = int(os.environ.get('DEV_PORT') or 3004)
    PROD_PORT = int(os.environ.get('PROD_PORT') or 80)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///simplechat_dev.db'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///simplechat.db'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///simplechat_test.db'

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}