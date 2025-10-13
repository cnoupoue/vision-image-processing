# Game Plate Vision Analyzer

This project analyzes a physical game board in real-time using **OpenCV**, detects and identifies the pieces present, and reconstructs their positions digitally.  
A **Flask** web server provides a live interface to visualize the detected board state.

## Features
- Real-time video capture and analysis with OpenCV  
- Game piece detection and classification  
- Flask-based web interface for visualization and interaction  
- Modular and extensible architecture  

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
