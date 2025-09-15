from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # 获取环境和端口配置
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'development':
        port = app.config.get('DEV_PORT', 3004)
        debug = True
    else:
        port = app.config.get('PROD_PORT', 80)
        debug = False
    
    print(f"启动 SimpleChat 应用...")
    print(f"环境: {env}")
    print(f"端口: {port}")
    print(f"调试模式: {debug}")
    print(f"访问地址: http://localhost:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )