import paho.mqtt.client as mqtt
from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory
import ssl

led = LED(17, pin_factory=LGPIOFactory())
led.off()

def on_message(client, userdata, msg):
    message = msg.payload.decode().strip()
    topic = msg.topic
    
    print(f"Received on {topic}: {message}")
    
    # ONLY act on commands from room/led
    if topic == "room/led":
        if message == "ON":
            led.on()
            print("LED turned ON")
            client.publish("room/led/status", "ON")
        elif message == "OFF":
            led.off()
            print("LED turned OFF")
            client.publish("room/led/status", "OFF")
    # Ignore room/led/status messages (they're just for the web UI)
    elif topic == "room/led/status":
        print(f"Ignoring status message: {message}")

# FIXED: Use new API version
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.username_pw_set("ibrmnas", "gecB7C!3Nq@fQ7n")
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.reconnect_delay_set(min_delay=1, max_delay=10)
client.on_message = on_message
client.connect("02265bce42164317af0133828c96f3db.s1.eu.hivemq.cloud", 8883, 60)

client.subscribe("room/led")
# Note: NOT subscribing to room/led/status to avoid loops

print("MQTT LED Controller started - waiting for commands...")
client.loop_forever()
