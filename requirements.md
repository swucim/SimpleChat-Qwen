# SimpleChat 需求文档

## 项目概述

SimpleChat 是一个基于大模型API的简单对话应用，提供用户友好的聊天界面，支持普通用户对话和管理员后台管理功能。

## 技术架构

### 后端技术栈
- **Web框架**: Flask
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy
- **API标准**: OpenAI API 规范
- **身份验证**: Flask-Login
- **配置管理**: Flask配置系统

### 前端技术栈
- **模板引擎**: Jinja2
- **样式框架**: 自定义CSS + Bootstrap (可选)
- **JavaScript**: 原生JS / jQuery
- **UI主色调**: #86BC25

### 大模型接口
- **默认服务商**: 硅基流动API
- **接口标准**: OpenAI API 规范
- **支持配置**: URL、API Key、模型名称

## 功能需求

### 1. 用户角色管理

#### 1.1 普通用户
- **免登录访问**: 无需注册登录即可使用对话功能
- **对话功能**: 与大模型进行实时对话
- **历史记录**: 查看个人对话历史记录
- **会话管理**: 创建新会话、删除会话
- **用户标识**: 基于浏览器会话的临时用户身份

#### 1.2 管理员用户
- **登录认证**: 管理员账号密码登录
- **用户管理**: 查看所有用户列表和基本信息
- **对话监控**: 查看所有用户的对话记录
- **接口配置**: 配置OpenAI接口信息(URL、Key、模型)
- **系统设置**: 管理系统基础配置
- **数据统计**: 查看系统使用统计信息

### 2. 对话功能

#### 2.1 核心对话
- **实时对话**: 支持流式响应显示
- **多轮对话**: 保持上下文连续性
- **消息类型**: 文本消息支持
- **错误处理**: 网络异常、API错误的友好提示

#### 2.2 会话管理
- **会话列表**: 显示用户的所有对话会话
- **会话创建**: 创建新的对话会话
- **会话删除**: 删除指定会话及其历史记录
- **会话重命名**: 支持自定义会话标题

### 3. 配置管理

#### 3.1 API配置
- **接口URL**: 可配置的API服务地址
- **API密钥**: 安全的密钥管理
- **模型选择**: 支持多种模型切换
- **默认配置**: 硅基流动API预设配置

#### 3.2 系统配置
- **端口配置**: 开发模式(3004)、生产模式(80)
- **数据库配置**: 不同环境的数据库设置
- **日志配置**: 系统运行日志管理

## 非功能需求

### 1. 性能要求
- **响应时间**: 页面加载时间 < 2秒
- **并发用户**: 支持100+并发用户
- **消息延迟**: 对话响应延迟 < 5秒

### 2. 安全要求
- **数据加密**: API密钥加密存储
- **访问控制**: 管理员功能访问控制
- **数据隔离**: 用户数据隔离保护
- **输入验证**: 防止XSS、SQL注入

### 3. 可用性要求
- **界面简洁**: 简约清晰的用户界面
- **响应式设计**: 支持桌面和移动端
- **错误提示**: 清晰的错误信息提示
- **操作反馈**: 及时的操作状态反馈

### 4. 部署要求
- **环境隔离**: 开发、测试、生产环境分离
- **配置管理**: 环境变量配置管理
- **容器化**: 支持Docker部署
- **监控日志**: 完整的运行日志记录

## 系统架构

### 1. 目录结构
```
SimpleChat-QWEN/
├── app/
│   ├── __init__.py          # Flask应用初始化
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模型
│   │   ├── conversation.py # 对话模型
│   │   └── message.py      # 消息模型
│   ├── views/              # 视图控制器
│   │   ├── __init__.py
│   │   ├── main.py         # 主页面路由
│   │   ├── chat.py         # 对话路由
│   │   └── admin.py        # 管理员路由
│   ├── services/           # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── chat_service.py # 对话服务
│   │   ├── api_service.py  # API接口服务
│   │   └── user_service.py # 用户服务
│   ├── static/             # 静态资源
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/          # 模板文件
│       ├── base.html
│       ├── chat.html
│       ├── admin/
│       └── components/
├── config/
│   ├── __init__.py
│   ├── development.py      # 开发环境配置
│   ├── production.py       # 生产环境配置
│   └── default.py          # 默认配置
├── migrations/             # 数据库迁移
├── tests/                  # 测试文件
├── logs/                   # 日志文件
├── requirements.txt        # Python依赖
├── run.py                  # 应用启动文件
├── wsgi.py                 # WSGI入口
├── Dockerfile              # Docker配置
├── docker-compose.yml      # Docker编排
├── README.md               # 项目说明
└── .env.example            # 环境变量示例
```

### 2. 数据库设计

#### 2.1 用户表 (users)
- id: 主键
- session_id: 会话标识
- is_admin: 管理员标识
- username: 用户名(管理员)
- password_hash: 密码哈希(管理员)
- created_at: 创建时间
- last_active: 最后活跃时间

#### 2.2 对话表 (conversations)
- id: 主键
- user_id: 用户ID(外键)
- title: 对话标题
- created_at: 创建时间
- updated_at: 更新时间

#### 2.3 消息表 (messages)
- id: 主键
- conversation_id: 对话ID(外键)
- role: 角色(user/assistant)
- content: 消息内容
- created_at: 创建时间

#### 2.4 配置表 (configs)
- id: 主键
- key: 配置键
- value: 配置值
- description: 配置描述
- updated_at: 更新时间

### 3. API设计

#### 3.1 前端API
- `GET /` - 主页面
- `GET /chat` - 对话页面
- `POST /api/chat/send` - 发送消息
- `GET /api/chat/history` - 获取历史记录
- `POST /api/chat/new` - 创建新会话
- `DELETE /api/chat/{id}` - 删除会话

#### 3.2 管理员API
- `GET /admin/login` - 登录页面
- `POST /admin/login` - 登录处理
- `GET /admin/dashboard` - 管理后台
- `GET /admin/users` - 用户列表
- `GET /admin/conversations` - 对话记录
- `POST /admin/config` - 配置更新

## 部署方案

### 1. 开发环境
- **端口**: 3004
- **数据库**: SQLite
- **调试模式**: 启用
- **热重载**: 启用

### 2. 生产环境
- **端口**: 80
- **数据库**: PostgreSQL
- **WSGI服务器**: Gunicorn
- **反向代理**: Nginx
- **容器化**: Docker

### 3. 环境变量
```
FLASK_ENV=development/production
DATABASE_URL=数据库连接字符串
SECRET_KEY=应用密钥
OPENAI_API_URL=API接口地址
OPENAI_API_KEY=API密钥
OPENAI_MODEL=模型名称
```

## 开发计划

### 第一阶段：基础框架搭建
1. Flask应用架构搭建
2. 数据库模型设计与创建
3. 基础路由和模板设置
4. 开发环境配置

### 第二阶段：核心功能开发
1. 用户会话管理
2. 对话功能实现
3. OpenAI API集成
4. 前端界面开发

### 第三阶段：管理功能开发
1. 管理员登录系统
2. 用户管理后台
3. 对话记录查看
4. 配置管理界面

### 第四阶段：优化与部署
1. 性能优化
2. 安全加固
3. 部署配置
4. 文档完善

## 质量保证

### 1. 测试策略
- **单元测试**: 核心业务逻辑测试
- **集成测试**: API接口测试
- **端到端测试**: 用户流程测试
- **性能测试**: 并发和负载测试

### 2. 代码质量
- **代码规范**: PEP8 Python编码规范
- **代码审查**: Pull Request审查机制
- **静态分析**: 代码质量检查工具
- **文档覆盖**: 完整的API和代码文档

### 3. 监控运维
- **日志监控**: 应用运行日志监控
- **性能监控**: 系统性能指标监控
- **错误追踪**: 异常错误跟踪系统
- **备份策略**: 数据定期备份策略