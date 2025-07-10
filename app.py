from app import create_app
from app.routes.auth import bp as auth_bp

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)