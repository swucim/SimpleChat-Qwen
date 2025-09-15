from app import db
from app import db
from datetime import datetime

class Config(db.Model):
    """配置模型"""
    __tablename__ = 'configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, key, value, description=None):
        self.key = key
        self.value = value
        self.description = description
    
    @staticmethod
    def get_value(key, default=None):
        """获取配置值"""
        config = Config.query.filter_by(key=key).first()
        return config.value if config else default
    
    @staticmethod
    def set_value(key, value, description=None):
        """设置配置值"""
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
            if description:
                config.description = description
        else:
            config = Config(key=key, value=value, description=description)
            db.session.add(config)
        db.session.commit()
        return config
    
    @staticmethod
    def get_openai_config():
        """获取OpenAI配置"""
        return {
            'api_url': Config.get_value('openai_api_url', ''),
            'api_key': Config.get_value('openai_api_key', ''),
            'model': Config.get_value('openai_model', 'Qwen/Qwen2-7B-Instruct')
        }
    
    @staticmethod
    def set_openai_config(api_url, api_key, model):
        """设置OpenAI配置"""
        Config.set_value('openai_api_url', api_url, 'OpenAI API URL')
        Config.set_value('openai_api_key', api_key, 'OpenAI API Key')
        Config.set_value('openai_model', model, 'OpenAI Model Name')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Config {self.key}: {self.value}>'