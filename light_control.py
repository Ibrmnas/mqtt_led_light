import paho.mqtt.client as mqtt
from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory
import ssl
import time
from datetime import datetime

# ---------------- CONFIG ----------------
MQTT_BROKER = "02265bce42164317af0133828c96f3db.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "ibrmnas"
MQTT_PASS = "gecB7C!3Nq@fQ7n"

TOPIC_CMD = "room/led"
TOPIC_STATUS = "room/led/status"

# ---------------- HARDWARE ----------------
led = LED(17, pin_factory=LGPIOFactory())
led.off()

last_state = None

# ---------------- HELPERS ----------------
def log_message(msg):
    """Add timestamp to log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def publish_state(client):
    state = "ON" if led.is_lit else "OFF"
    client.publish(TOPIC_STATUS, state, retain=True)
    log_message(f"Published state: {state}")

def set_led(state, client):
    global last_state

    if state == last_state:
        return

    last_state = state

    if state == "ON":
        led.on()
        log_message("?? LED turned ON")
    elif state == "OFF":
        led.off()
        log_message("?? LED turned OFF")

    publish_state(client)

# ---------------- MQTT CALLBACKS ----------------
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        log_message("? Connected to MQTT broker")
        client.subscribe(TOPIC_CMD)
        publish_state(client)
    else:
        log_message(f"? Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        if msg.topic != TOPIC_CMD:
            return

        message = msg.payload.decode().strip()
        log_message(f"?? Received command: {message}")

        if message in ["ON", "OFF"]:
            set_led(message, client)
        else:
            log_message(f"?? Unknown command: {message}")

    except Exception as e:
        log_message(f"? Error: {e}")

def on_disconnect(client, userdata, rc, properties=None):
    log_message("?? Disconnected from MQTT broker. Reconnecting...")

# ---------------- MQTT CLIENT ----------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.reconnect_delay_set(min_delay=1, max_delay=10)

# Set Last Will (informs when Pi disconnects unexpectedly)
client.will_set(TOPIC_STATUS, "OFFLINE", retain=True)

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# ---------------- CONNECT LOOP ----------------
while True:
    try:
        log_message("?? Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except Exception as e:
        log_message(f"? Connection failed: {e}")
        time.sleep(5)

# ---------------- START LOOP ----------------
log_message("?? MQTT LED Controller running")
client.loop_forever()
