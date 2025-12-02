from flask import Blueprint, Response, render_template, jsonify
import cv2
from camera.camera import Camera
from game.engine import game_instance  # Import du jeu
from game.visualizer import draw_game_state  # Import du peintre
from game.controller import get_video_stream_generator, get_camera_status

video_bp = Blueprint('video_bp', __name__)
#camera = Camera()


@video_bp.route('/')
def index():
    return render_template('index.html')


@video_bp.route('/status')
def status():
    return jsonify({
        'detected': get_camera_status()
    })

@video_bp.route('/video_feed')
def video_feed():
    return Response(get_video_stream_generator(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')