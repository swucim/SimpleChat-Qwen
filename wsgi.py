from app import create_app

# WSGI应用入口点
application = create_app('production')

if __name__ == "__main__":
    application.run()