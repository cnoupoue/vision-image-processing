from flask import Blueprint, Response, render_template
from camera import Camera

video_bp = Blueprint('video', __name__)
camera = Camera()

@video_bp.route('/')
def index():
    return render_template('index.html')

@video_bp.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

