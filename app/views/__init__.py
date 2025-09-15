# 导入所有视图蓝图，便于其他模块使用
from .main import main
from .chat import chat
from .admin import admin

__all__ = ['main', 'chat', 'admin']