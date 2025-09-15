@echo off
echo === SimpleChat 开发环境启动脚本 ===

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 检查环境变量文件
if not exist ".env" (
    echo 创建环境变量文件...
    copy .env.example .env
    echo 请编辑 .env 文件配置API密钥等信息
)

REM 初始化数据库
echo 初始化数据库...
set FLASK_ENV=development
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('数据库初始化完成')"

REM 启动应用
echo 启动 SimpleChat 开发服务器...
echo 访问地址: http://localhost:3004
echo 管理后台: http://localhost:3004/admin/login
echo 默认管理员账号: admin / admin123
echo.
echo 按 Ctrl+C 停止服务器
echo.

python run.py

pause