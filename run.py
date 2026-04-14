from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # En Docker, écouter sur 0.0.0.0 pour être accessible de l'hôte
    # En développement local, utiliser 127.0.0.1
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=True)