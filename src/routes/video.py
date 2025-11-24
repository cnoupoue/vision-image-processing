from flask import Blueprint, Response, render_template, jsonify
from camera.camera import Camera

video_bp = Blueprint('video_bp', __name__)
camera = Camera()

@video_bp.route('/')
def index():
    return render_template('index.html')

@video_bp.route('/status')
def status():
    return jsonify({
        'detected': camera.is_board_detected
    })

@video_bp.route('/video_feed')
def video_feed():
    return Response(camera.generate_jpeg_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')