## Image Capture and MQTT Publisher

This project captures images using a camera connected to a Raspberry Pi, publishes them to an MQTT broker, and stores them locally if the MQTT connection fails.

### Prerequisites (Raspberry Pi)

- **Hardware**: Raspberry Pi with a connected camera module.
- **Software**:
  - Python 3
  - picamera
  - Paho MQTT
  - MQTT Server connection

**Install Dependencies**

Install required Python packages using pip:

```bash
pip install picamera paho-mqtt
```

**Run the Script**

```bash
python capture_image.py
```

---

## Alternatively,

### Prerequisites (Any OS for testing)

- **Hardware**: Linux/Windows/Mac.
- **Software**:
  - Python 3
  - OpenCV
  - Paho MQTT
  - MQTT Server connection

**Install Dependencies**

Install required Python packages using pip:

```bash
pip install opencv-python paho-mqtt
```

**Run the Script**

```bash
python capture_image_cv2.py
```
