# Game Plate Vision Analyzer

This project analyzes a physical game board in real-time using **OpenCV**, detects and identifies the pieces present, and reconstructs their positions digitally.  
A **Flask** web server provides a live interface to visualize the detected board state.

## Features
- Real-time video capture and analysis with OpenCV  
- Game piece detection and classification  
- Flask-based web interface for visualization and interaction  
- Modular and extensible architecture  

## How It Works

This project uses your **iPhone as a webcam** through **Continuity Camera** (macOS) or **Camo Virtual Driver** (Windows).  
No extra apps need to be running — the system handles everything automatically.

### System Integration

macOS and Windows expose the iPhone as a **standard UVC (USB Video Class) webcam** using a built-in or virtual driver.  
This means OpenCV can access it like any normal webcam — no manual setup required.

### OpenCV

`cv2.VideoCapture()` simply requests the first available camera from the OS.  
The system returns the virtual iPhone camera (e.g., *“Camo Studio Virtual Camera”* or *“Continuity Camera”*).  
OpenCV reads frames directly from this virtual webcam.

### Flask Streaming

The video frames are encoded as JPEGs and streamed over HTTP using an **MJPEG feed**.  
The browser displays this live feed in real time at `/video_feed`.

### Summary

| Component | Role |
|------------|------|
| **iPhone** | Captures the video feed |
| **OS driver (Continuity / Camo)** | Exposes iPhone as a virtual webcam |
| **OpenCV** | Reads frames from the virtual camera |
| **Flask** | Streams frames to the web |
| **Browser** | Displays the live feed |

## Tech Stack
- **Python 3.x**
- **Flask**
- **OpenCV (cv2)**
- **Numpy**

## Prerequisites

Before getting started, make sure you have the following installed on your machine:

- [Docker](https://www.docker.com/products/docker-desktop) - Container management
- [Docker Compose](https://docs.docker.com/compose/) - Container orchestration
- [Git](https://git-scm.com/) - To clone the repository
- [Python 3](https://www.python.org/) - Required for the Data Mining service- Docker
- [Camo Studio](camo.studio) - Required to get the webcam of your phone as a driver on your laptop

You'll also need Camo Video on your iPhone

## Installation

For Linux/macOS

```bash
make install
make up
make docker-build
make docker-up
```

For Windows

```bash
setup.bat install
setup.bat up
setup.bat docker-build
setup.bat docker-up
``` 

## Authors

- [Jobelin KOM](https://linkedin.com/in/jobelin-kom/).
- [Cameron NOUPOUE](https://linkedin.com/in/cnoupoue/).

## Credits 

Project devised and created during my studies at the Haute-Ecole de la Province de Liège (HEPL), Belgium.

## Licenses

This project is licensed under the [MIT license](https://mit-license.org/).
