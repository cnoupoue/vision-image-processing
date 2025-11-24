from flask import Flask
from routes.video import video_bp
from routes.game import game_bp

app = Flask(__name__)
app.register_blueprint(video_bp, url_prefix='/')
app.register_blueprint(game_bp, url_prefix='/game')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
