# aruco-kinect

> ROS 2 node for ArUco marker detection and 6-DoF pose estimation via the Azure Kinect RGB camera.

[![ROS 2](https://img.shields.io/badge/ROS%202-Humble-blue?style=flat-square)](https://docs.ros.org/en/humble/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=flat-square)](https://www.python.org/)

## Overview

This package subscribes to the RGB image stream published by the [Azure Kinect ROS driver](https://github.com/microsoft/Azure_Kinect_ROS_Driver), detects [ArUco](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html) markers in each frame using OpenCV, and estimates their 6-DoF pose (translation + rotation) relative to the camera. The annotated image is re-published for visualization in RViz or rqt.

**Key behaviors:**
- Detects markers from the `DICT_5X5_100` dictionary
- Estimates pose per marker using `cv2.aruco.estimatePoseSingleMarkers`
- Logs translation and rotation vectors to the ROS logger
- Publishes the annotated frame for real-time visualization

> [!NOTE]
> The camera intrinsics (`camera_matrix` and `distortion_coefficients`) in `arucodetect.py` are calibrated for a specific Azure Kinect unit. You must replace them with the values from your own camera calibration before use.

## Requirements

| Dependency | Version |
|---|---|
| ROS 2 | Humble (or newer) |
| [Azure Kinect ROS Driver](https://github.com/microsoft/Azure_Kinect_ROS_Driver) | latest |
| OpenCV | 4.x (with `aruco` contrib module) |
| `cv_bridge` | — |
| Python | 3.10+ |

## Installation

Clone this repository into your ROS 2 workspace `src/` directory and build:

```bash
cd ~/ros2_ws/src
git clone https://github.com/rubi/aruco-kinect.git
cd ..
colcon build --packages-select aruco
source install/setup.bash
```

## Configuration

Before running the node, open `aruco/arucodetect.py` and replace the hardcoded camera intrinsics with the calibration data for your Azure Kinect:

```python
# Camera matrix (K) — replace with your calibration values
self.camera_matrix = np.array([[fx,  0, cx],
                               [ 0, fy, cy],
                               [ 0,  0,  1]])

# Distortion coefficients (k1, k2, p1, p2, k3)
self.distortion_coefficients = np.array([k1, k2, p1, p2, k3])
```

You can obtain these values by running the Azure Kinect's built-in calibration tool or by using the `camera_info` topic published by the ROS driver.

## Usage

**1. Start the Azure Kinect driver:**

```bash
ros2 launch azure_kinect_ros_driver driver.launch.py
```

**2. Run the ArUco detection node:**

```bash
ros2 run aruco aruco
```

**3. Visualize the output in rqt:**

```bash
rqt_image_view /image_display
```

### Topics

| Topic | Direction | Type | Description |
|---|---|---|---|
| `rgb/image_raw` | Subscribed | `sensor_msgs/Image` | Raw RGB frames from the Kinect |
| `image_display` | Published | `sensor_msgs/Image` | Annotated frames with detected markers |

## Marker Setup

Print any marker from the `DICT_5X5_100` dictionary. The default marker size used for pose estimation is **2 cm** (`0.02 m`). If your printed markers are a different size, update the marker length parameter in `estimatePoseSingleMarkers`:

```python
rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
    corners[i],
    0.05,  # <-- your marker size in meters
    self.camera_matrix,
    self.distortion_coefficients
)
```

> [!TIP]
> You can generate printable ArUco markers at [chev.me/arucogen](https://chev.me/arucogen/) — select dictionary **5x5** and any ID from 0 to 99.
