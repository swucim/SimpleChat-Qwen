# SimpleChat - 基于大模型的智能对话应用

![SimpleChat](https://img.shields.io/badge/SimpleChat-v1.0-86BC25)
![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

SimpleChat 是一个基于大模型API的简单对话应用，提供用户友好的聊天界面，支持普通用户对话和管理员后台管理功能。

## ✨ 功能特色

### 🔥 核心功能
- **智能对话**: 基于大语言模型，支持自然流畅的多轮对话
- **即用即走**: 无需注册登录，打开即可使用
- **历史记录**: 自动保存对话历史，支持多会话管理
- **响应式设计**: 完美适配桌面端和移动端

### 👥 用户角色
- **普通用户**: 免登录对话，查看个人历史记录
- **管理员**: 用户管理、对话监控、系统配置

### 🛠 管理功能
- **用户管理**: 查看所有用户信息和活动状态
- **对话监控**: 查看所有对话记录和详细内容
- **API配置**: 动态配置大模型API接口
- **数据统计**: 实时系统使用统计

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip (Python包管理器)
- 大模型API密钥 (推荐硅基流动)

### 安装步骤

#### Windows用户
1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/SimpleChat-QWEN.git
   cd SimpleChat-QWEN
   ```

2. **一键启动**
   ```bash
   start_dev.bat
   ```

#### Linux/Mac用户
1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/SimpleChat-QWEN.git
   cd SimpleChat-QWEN
   ```

2. **一键启动**
   ```bash
   chmod +x start_dev.sh
   ./start_dev.sh
   ```

#### 手动安装
1. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置API密钥
   ```

4. **启动应用**
   ```bash
   python run.py
   ```

### 访问应用
- **主应用**: http://localhost:3004
- **管理后台**: http://localhost:3004/admin/login
- **默认管理员**: admin / admin123

## ⚙️ 配置说明

### 环境变量配置
复制 `.env.example` 为 `.env` 并配置以下参数：

```env
# 开发环境配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///simplechat.db

# OpenAI API 配置
OPENAI_API_URL=https://api.siliconflow.cn/v1/chat/completions
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=Qwen/Qwen2-7B-Instruct

# 服务器配置
DEV_PORT=3004
PROD_PORT=80

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 支持的API服务商

| 服务商 | API地址 | 推荐模型 |
|--------|---------|----------|
| 硅基流动 | `https://api.siliconflow.cn/v1/chat/completions` | Qwen/Qwen2-7B-Instruct |
| OpenAI | `https://api.openai.com/v1/chat/completions` | gpt-3.5-turbo |
| 其他兼容服务 | 自定义URL | 对应模型名称 |

### 获取API密钥

#### 硅基流动 (推荐)
1. 访问 [硅基流动官网](https://siliconflow.cn/)
2. 注册账号并完成认证
3. 在控制台创建API密钥
4. 复制密钥到配置文件

#### OpenAI
1. 访问 [OpenAI官网](https://openai.com/)
2. 注册账号并购买额度
3. 在API设置中创建密钥
4. 复制密钥到配置文件

## 🏗️ 项目结构

```
SimpleChat-QWEN/
├── app/                    # 应用主目录
│   ├── __init__.py        # Flask应用工厂
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── conversation.py # 对话模型
│   │   ├── message.py     # 消息模型
│   │   └── config_model.py # 配置模型
│   ├── views/             # 视图控制器
│   │   ├── main.py        # 主页面路由
│   │   ├── chat.py        # 对话API路由
│   │   └── admin.py       # 管理员路由
│   ├── services/          # 业务逻辑层
│   │   ├── api_service.py # API接口服务
│   │   ├── chat_service.py # 对话服务
│   │   └── user_service.py # 用户服务
│   ├── static/            # 静态资源
│   │   ├── css/          # 样式文件
│   │   ├── js/           # JavaScript文件
│   │   └── images/       # 图片文件
│   └── templates/         # 模板文件
│       ├── base.html     # 基础模板
│       ├── index.html    # 首页模板
│       ├── chat.html     # 对话页面
│       └── admin/        # 管理员模板
├── config/                # 配置文件
├── migrations/            # 数据库迁移
├── tests/                 # 测试文件
├── logs/                  # 日志文件
├── requirements.txt       # Python依赖
├── run.py                # 开发环境启动
├── wsgi.py               # 生产环境WSGI
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker编排文件
├── start_dev.bat         # Windows启动脚本
├── start_dev.sh          # Linux/Mac启动脚本
└── README.md             # 项目说明
```

## 🐳 Docker部署

### 开发环境
```bash
# 构建镜像
docker build -t simplechat .

# 运行容器
docker run -p 3004:80 \
  -e OPENAI_API_KEY=your-api-key \
  simplechat
```

### 生产环境
```bash
# 使用docker-compose
docker-compose up -d
```

## 🔧 API接口

### 对话API
- `GET /api/chat/conversations` - 获取对话列表
- `POST /api/chat/new` - 创建新对话
- `GET /api/chat/messages/<id>` - 获取对话消息
- `POST /api/chat/send` - 发送消息
- `DELETE /api/chat/delete/<id>` - 删除对话

### 管理员API
- `POST /admin/login` - 管理员登录
- `GET /admin/dashboard` - 管理面板
- `GET /admin/users` - 用户管理
- `GET /admin/conversations` - 对话管理
- `POST /admin/config` - 系统配置

## 🎨 界面预览

### 主界面
- 简洁的对话界面，主色调 #86BC25
- 左侧对话列表，右侧消息区域
- 支持移动端响应式布局

### 管理后台
- 专业的管理界面
- 数据统计图表
- 用户和对话管理功能

## 🔐 安全特性

- **API密钥加密**: 数据库存储加密的API密钥
- **会话管理**: 安全的用户会话管理
- **权限控制**: 管理员功能访问控制
- **输入验证**: 防止XSS和SQL注入攻击

## 🚀 生产部署

### 方式1: 传统部署
1. **服务器准备**
   - Python 3.7+ 环境
   - PostgreSQL 数据库
   - Nginx 反向代理

2. **应用部署**
   ```bash
   # 克隆代码
   git clone https://github.com/your-username/SimpleChat-QWEN.git
   cd SimpleChat-QWEN
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置环境变量
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@localhost/simplechat
   
   # 启动应用
   gunicorn --bind 0.0.0.0:80 --workers 4 wsgi:application
   ```

### 方式2: Docker部署
```bash
# 使用docker-compose一键部署
docker-compose up -d
```

### 方式3: 云平台部署
支持部署到各种云平台：
- Heroku
- AWS
- 阿里云
- 腾讯云

## 📝 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✅ 基础对话功能
- ✅ 用户会话管理
- ✅ 管理员后台
- ✅ API配置功能
- ✅ Docker支持

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 常见问题

### Q: 如何更换API服务商？
A: 在管理后台的"系统配置"页面可以动态更换API地址、密钥和模型。

### Q: 忘记管理员密码怎么办？
A: 可以修改 `.env` 文件中的 `ADMIN_PASSWORD`，然后重启应用。

### Q: 如何清理历史数据？
A: 可以在管理后台查看和管理用户对话数据，或直接操作数据库。

### Q: 支持哪些大模型？
A: 支持所有兼容OpenAI API格式的模型服务，包括GPT系列、Qwen系列等。

## 💬 技术支持

- **问题反馈**: [GitHub Issues](https://github.com/your-username/SimpleChat-QWEN/issues)
- **功能建议**: [GitHub Discussions](https://github.com/your-username/SimpleChat-QWEN/discussions)
- **技术交流**: 欢迎star和fork本项目

## 🙏 致谢

感谢以下开源项目的支持：
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM框架
- [Bootstrap](https://getbootstrap.com/) - UI组件
- [OpenAI](https://openai.com/) - API标准

---

如果这个项目对您有帮助，请给个 ⭐️ 支持一下！