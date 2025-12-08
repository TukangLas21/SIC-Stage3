import paho.mqtt.client as mqtt
import json
import pandas as pd
import joblib
import os
from datetime import datetime

# --- KONFIGURASI ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_SENSOR = "iot/sensor/data"
TOPIC_OUTPUT = "iot/output"
MODEL_FILE = "iot_temp_model.pkl"
CSV_FILE = "sensor_log.csv"

# Load Model ML
print(f"Loading model {MODEL_FILE}...")
try:
    model = joblib.load(MODEL_FILE)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Fungsi Log ke CSV
def log_to_csv(timestamp, temp, hum, pred):
    file_exists = os.path.isfile(CSV_FILE)
    
    df = pd.DataFrame([{
        'timestamp': timestamp,
        'temperature': temp,
        'humidity': hum,
        'predicted_label': pred
    }])
    
    # Append mode, header hanya jika file belum ada
    df.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False)

# Callback saat pesan masuk
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        
        temp = data.get('temp')
        hum = data.get('hum')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Prediksi menggunakan Model
        # Input model harus DataFrame/array 2D [[temp, hum]]
        prediction = model.predict([[temp, hum]])[0] # Hasil: 'Normal' atau 'Panas'
        
        # 2. Tampilkan di Console
        print(f"[{timestamp}] Temp: {temp}°C, Hum: {hum}% -> Prediksi: {prediction}")
        
        # 3. Log ke CSV
        log_to_csv(timestamp, temp, hum, prediction)
        
        # 4. Trigger Output ke ESP32
        if prediction == "Panas":
            client.publish(TOPIC_OUTPUT, "BUZZER_ON")
            print(">> Command Sent: BUZZER_ON")
        else:
            client.publish(TOPIC_OUTPUT, "BUZZER_OFF")
            print(">> Command Sent: BUZZER_OFF")
            
    except Exception as e:
        print(f"Error processing data: {e}")

# Setup MQTT Client
client = mqtt.Client()
client.on_message = on_message

print(f"Connecting to MQTT Broker {MQTT_BROKER}...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(TOPIC_SENSOR)
print(f"Subscribed to {TOPIC_SENSOR}")

# Loop forever
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nDisconnecting...")
    client.disconnect()