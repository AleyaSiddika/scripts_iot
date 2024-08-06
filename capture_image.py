import time
import os
from datetime import datetime
from picamera import PiCamera
import paho.mqtt.client as mqtt

# MQTT Broker Information from Environment Variables
BROKER_URL = os.environ.get('MQTT_URL', 'mqtt.student2307277.rahtiapp.fi')
BROKER_PORT = int(os.environ.get('MQTT_PORT', 443))
CLIENT_ID = os.environ.get('CLIENT_ID', 'student2307277-client')
INTERVAL = os.environ.get('INTERVAL', 1)

is_connected = False

# Initialize Camera
camera = PiCamera()
camera.resolution = (1024, 768)

def capture_and_publish_image(client):
    try:
        while True:
            # Capture image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f'captured_image_{timestamp}.jpg'
            camera.capture(image_filename)
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
            else: #noqa
                print(f"MQTT not connected. Storing image locally as '{image_filename}'.")
  
            # Wait 1 second before capturing the next image
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("Stopping image capture...")
    finally:
        camera.close()

def main():
    # Configure MQTT client
    client = mqtt.Client(CLIENT_ID)
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
