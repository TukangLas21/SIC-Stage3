import paho.mqtt.client as mqtt
import json
import pandas as pd
import joblib
import os
from datetime import datetime, time
import argparse

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_SENSOR = "SamsungPintar/data"
MODEL_FILE = "iot_temp_model.pkl"
CSV_FILE = "sensor_log_gather.csv"

label = 'dingin'

# Fungsi Log ke CSV
def log_to_csv(timestamp, temp, hum, pred):
    file_exists = os.path.isfile(CSV_FILE)
    
    df = pd.DataFrame([{
        'timestamp': timestamp,
        'temperature': temp,
        'humidity': hum,
        'label': pred
    }])
    
    # Append mode, header hanya jika file belum ada
    df.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False)

# Callback saat pesan masuk
def on_message(client, userdata, msg):
    try:
        print("Message received!")
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        temp = data.get('temperature')
        hum = data.get('humidity')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        
        print(f"[{timestamp}] Temp: {temp}°C, Hum: {hum}%")
        
        log_to_csv(timestamp, temp, hum, label)
        
    except Exception as e:
        print(f"Error processing data: {e}")

# Callback when connected
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC_SENSOR)
    print(f"Subscribed to {TOPIC_SENSOR}")

# Setup MQTT Client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to MQTT Broker {MQTT_BROKER}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Loop forever
try:
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-l',
        '--label',
        type=str,
        default='dingin',
        help='Set label for data sample'
        )
    
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        default=CSV_FILE,
        help='Set CSV log file name'
    )
    args = parser.parse_args()
    label = args.label
    CSV_FILE = args.file
    client.loop_forever()
except KeyboardInterrupt:
    print("\nDisconnecting...")
    client.disconnect()