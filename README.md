# vision-image-processing
A computer vision project that analyzes a game board in real-time using OpenCV to detect and reconstruct the positions of game pieces. The system runs on a Flask server for live visualization and interaction.

## Features

- 📷 **Real-Time Detection**: Continuously monitor and analyze game board positions
- 🔍 **Piece Recognition**: Advanced algorithms for identifying game pieces
- 🎨 **Live Visualization**: Interactive Flask-based web interface
- ⚡ **Fast Processing**: Optimized OpenCV algorithms for quick analysis

## Technology Stack

- **Python**: Core programming language
- **Flask**: Web server framework for live interaction
- **OpenCV**: Computer vision library for image processing

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/cnoupoue/vision-image-processing.git
cd vision-image-processing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

Start the Flask server:
```bash
python app.py
```

The server will start on `http://localhost:5000`. Open your web browser and navigate to this address to view the landing page.

## Project Structure

```
vision-image-processing/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── templates/            
│   └── index.html        # Landing page template
├── static/
│   └── css/
│       └── style.css     # Styling for the web interface
├── README.md             # Project documentation
└── LICENSE               # MIT License
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Cameron - [GitHub Profile](https://github.com/cnoupoue)
