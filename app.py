"""
Flask server for vision-image-processing project.
Provides a web interface for real-time game board analysis using computer vision.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    """Render the landing page explaining the project purpose."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
