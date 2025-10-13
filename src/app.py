from flask import Flask
from routes.video import video_bp

app = Flask(__name__)
app.register_blueprint(video_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
