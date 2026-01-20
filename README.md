# Monopoly Vision AR (Naruto Edition)

**Monopoly Vision AR** is a hybrid project combining **Computer Vision**, **Game Logic**, and **Augmented Reality**. It analyzes a physical Monopoly board in real-time, detects dice rolls, enforces game rules autonomously, and projects interactive animations back onto the video feed.

A **Flask** web server provides a live interface to visualize the game state, manage players, and interact with the physical board.

## Assignment Due Date

## Features

### 🎮 Game Mechanics

* **Automated Dice Detection:** Detects physical dice rolls and moves tokens automatically.
* **Complete Monopoly Logic:** Handles property buying, rent payments, taxes, and "Go to Jail" mechanics.
* **Economic System:** Automatic money transfer between players and the bank.
* **Interactive Web Interface:** Buttons to buy properties, start the game, or end turns manually.

### ✨ Augmented Reality (AR)

* **Real-time Board Tracking:** The system locks onto the board regardless of camera angle.
* **Dynamic Overlays:**
* **Property Ownership:** Owned squares are highlighted in the player's color.
* **Token Animation:** Smooth movement interpolation (tokens "hop" from square to square).
* **Floating Text:** Financial transactions (`+200$`, `-50$`) float above the board.
* **Visual Effects:** Flash effects on purchase, "Ninja Smoke" animation when going to jail, and pulsing aura for the active player.



## Technical Approach & Image Processing

This project leverages advanced image processing techniques using **OpenCV** to bridge the physical and digital worlds.

### 1. Computer Vision Module (`camera.py`)

* **Board Detection:**
* Uses **Gaussian Blur** and **Canny Edge Detection** to find contours.
* Applies **Polygon Approximation (approxPolyDP)** to identify the 4 corners of the board.
* Enhances contrast using **CLAHE** (Contrast Limited Adaptive Histogram Equalization) for low-light conditions.


* **Perspective Transformation:**
* Computes a **Homography Matrix** to warp the perspective.
* Transforms the angled camera view into a perfect top-down (bird's-eye) view (`warpPerspective`).


* **Dice Detection:**
* Uses **Otsu’s Binarization** (Adaptive Thresholding) to isolate dice pips.
* Filters blobs based on circularity and area to count the score.
* Implements **Temporal Stabilization**: Waits for the dice value to be stable for consecutive frames before triggering an action.



### 2. Game Engine (`engine.py`)

* Implements a **State Machine** (`WAITING_ROLL`, `MOVED`, `CAN_BUY`) to synchronize physical actions with digital rules.
* Maps the 40 Monopoly squares to specific coordinates relative to the detected board corners.

### 3. AR Visualization (`visualizer.py`)

* Projects game data back onto the video feed using the inverse homography or direct overlay on the warped image.
* Uses **Alpha Blending** (`cv2.addWeighted`) for transparent overlays and colorful borders.

## Tech Stack

* **Language:** Python 3.x
* **Computer Vision:** OpenCV (cv2), Numpy
* **Backend:** Flask (Web Server & Streaming)
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Containerization:** Docker

## Project Architecture

```plaintext
├── src
│   ├── game
│   │   ├── board_data.py   # Data model (40 squares, prices, types, coordinates)
│   │   ├── engine.py       # Core Logic (Rules, Player State, Economy)
│   │   ├── controller.py   # Main Loop (Orchestrates Camera, Engine, and Visualizer)
│   │   ├── visualizer.py   # AR Renderer (Draws tokens, effects, and overlays)
│   │   └── dice.py         # Dice Detection Logic
│   ├── routes
│   │   ├── video.py        # MJPEG Streaming Route
│   │   └── game.py         # API Routes for Frontend interaction (Buy, Roll, etc.)
│   └── camera
│       └── camera.py       # Image Processing (Homography, Contours, Stabilization)

```

## Hardware Setup

This project uses your **Smartphone** as a high-quality webcam through **Continuity Camera** (macOS) or **Camo Virtual Driver** (Windows).

| Component | Role |
| --- | --- |
| **Smartphone** | Captures the video feed (high resolution). |
| **Camo / Continuity** | Exposes the phone as a standard USB Webcam driver. |
| **OpenCV** | Reads frames from the virtual camera index (usually 0 or 1). |

## Installation

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop)
* [Python 3](https://www.python.org/)
* [Camo Studio](https://www.google.com/search?q=https://camo.studio) (or equivalent webcam software)

### Quick Start

**For Linux/macOS:**

```bash
make install
make up
# To run via Docker:
make docker-build
make docker-up

```

**For Windows:**

```bash
setup.bat install
setup.bat up
# To run via Docker:
setup.bat docker-build
setup.bat docker-up

```

## Authors

* [Jobelin KOM](https://linkedin.com/in/jobelin-kom/)
* [Cameron NOUPOUE](https://linkedin.com/in/cnoupoue/)

## Credits

Project devised and created during computer science studies at the **Haute-Ecole de la Province de Liège (HEPL)**, Belgium.

## Licenses

This project is licensed under the [MIT license](https://mit-license.org/).