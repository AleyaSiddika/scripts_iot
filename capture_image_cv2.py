import time
import os
from datetime import datetime
import cv2
import paho.mqtt.client as mqtt

# MQTT Broker Information from Environment Variables
# MQTT Broker Information from Environment Variables
BROKER_URL = os.environ.get('MQTT_URL', 'mqtt.student2307277.rahtiapp.fi')
BROKER_PORT = int(os.environ.get('MQTT_PORT', 443))
CLIENT_ID = os.environ.get('CLIENT_ID', 'student2307277-client')
INTERVAL = float(os.environ.get('INTERVAL', 1))

is_connected = False

# Initialize Camera using OpenCV
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

def capture_and_publish_image(client):
    try:
        while True:
            # Capture image from the camera
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image.")
                continue

            # Generate timestamp for the image filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f'captured_image_{timestamp}.jpg'

            # Save the image
            cv2.imwrite(image_filename, frame)
            print(f"Image captured and saved as '{image_filename}'.")

            if is_connected:
                try:
                    # Read the image file
                    with open(image_filename, "rb") as image_file:
                        image_data = image_file.read()

                    # Publish the image
                    client.publish(topic=f"{CLIENT_ID}/camera/{timestamp}", payload=image_data, qos=0, retain=False)
                    print(f"Image published to MQTT topic '{CLIENT_ID}/camera/{timestamp}'.")

                    # Remove the image file after publishing
                    os.remove(image_filename)

                except Exception as e:
                    print(f"Failed to publish image: {e}")
                    # If publish fails, keep the file for retry or local storage
            else:
                print(f"MQTT not connected. Storing image locally as '{image_filename}'.")

            # Wait for the specified interval before capturing the next image
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Stopping image capture...")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def main():
    # Configure MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, CLIENT_ID)
    client.tls_set("ca.crt")
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    
    client.connect(BROKER_URL, BROKER_PORT)
    client.loop_start()
    
    # Wait for the connection
    while not is_connected:
        print("Connecting to MQTT broker...")
        time.sleep(5)
    
    # Start capturing and publishing images
    capture_and_publish_image(client)

    client.loop_stop()
    client.disconnect()

def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        is_connected = True
        print("Connected to broker")
    else:
        print(f"Failed to connect with result code {rc}")

def on_disconnect(client, userdata, rc):
    global is_connected
    is_connected = False
    if rc != 0:
        print("Unexpected disconnection.")

def on_publish(client, userdata, mid):
    print(f"Message with ID {mid} published.")

if __name__ == "__main__":
    main()