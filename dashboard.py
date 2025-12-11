import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import queue
import pandas as pd
import plotly.express as px

# ================= KONFIGURASI =================
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_SENSOR = "SamsungPintar/data"
TIMEOUT_THRESHOLD = 5 

# ================= SETUP HALAMAN =================
st.set_page_config(page_title="IoT Dashboard Monitor", page_icon="🌡️", layout="wide")
st.title("🌡️ IoT Sensor Monitoring & Realtime Charts")

# ================= INISIALISASI STATE =================
if "data_queue" not in st.session_state:
    st.session_state["data_queue"] = queue.Queue()

if "data_log" not in st.session_state:
    st.session_state["data_log"] = []

if "last_packet" not in st.session_state:
    st.session_state["last_packet"] = None

if "broker_connected" not in st.session_state:
    st.session_state["broker_connected"] = False

if "last_update_time" not in st.session_state:
    st.session_state["last_update_time"] = 0

# ================= FUNGSI MQTT =================
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        userdata.put(("STATUS", True))

def on_disconnect(client, userdata, flags, reason_code, properties):
    userdata.put(("STATUS", False))

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        userdata.put(("DATA", data))
    except Exception as e:
        print(f"Error parsing json: {e}")

# ================= SETUP CLIENT =================
if "mqtt_client" not in st.session_state:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=st.session_state["data_queue"])
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(TOPIC_SENSOR)
        client.loop_start()
        st.session_state["mqtt_client"] = client
    except Exception as e:
        st.error(f"Gagal koneksi MQTT: {e}")

# ================= BAGIAN DINAMIS (FRAGMENT) =================
@st.fragment(run_every=1)
def update_dashboard():
    while not st.session_state["data_queue"].empty():
        try:
            msg_type, content = st.session_state["data_queue"].get_nowait()
            
            if msg_type == "STATUS":
                st.session_state["broker_connected"] = content
                
            elif msg_type == "DATA":
                st.session_state["last_update_time"] = time.time()
                current_time = datetime.now().strftime("%H:%M:%S")
                
                new_record = {
                    "timestamp": current_time,
                    "temperature": content.get("temperature", 0),
                    "humidity": content.get("humidity", 0),
                    "predicted_label": content.get("label", "unknown")
                }
                
                st.session_state["last_packet"] = new_record
                st.session_state["data_log"].append(new_record)
                
                if len(st.session_state["data_log"]) > 100:
                    st.session_state["data_log"].pop(0)
                    
        except queue.Empty:
            pass

    # 2. TAMPILAN HEADER STATUS
    st.markdown("### 🔌 Status Sistem")
    col_stat1, col_stat2, col_stat3 = st.columns(3)

    with col_stat1:
        if st.session_state["broker_connected"]:
            st.success("✅ MQTT Broker: Terhubung")
        else:
            st.error("❌ MQTT Broker: Terputus")

    time_since_last = time.time() - st.session_state["last_update_time"]
    is_device_online = time_since_last < TIMEOUT_THRESHOLD and st.session_state["last_packet"] is not None

    with col_stat2:
        if is_device_online:
            st.success(f"✅ ESP32 Sensor: Online ({int(time_since_last)}s ago)")
        else:
            st.warning(f"⚠️ ESP32 Sensor: Offline ({int(time_since_last)}s)")

    with col_stat3:
        if st.button("🗑️ Reset Data"):
            st.session_state["data_log"] = []
            st.rerun() 

    st.markdown("---")

    # 3. TAMPILAN UTAMA (METRICS & CHARTS)
    last_data = st.session_state["last_packet"]
    
    if last_data:
        c1, c2, c3 = st.columns(3)
        c1.metric("Temperature", f"{last_data['temperature']} °C")
        c2.metric("Humidity", f"{last_data['humidity']} %")
        
        with c3:
            lbl = last_data['predicted_label']
            if lbl == "panas":
                st.markdown(f"### :red[{lbl}] ⚠️")
            elif lbl == "dingin":
                st.markdown(f"### :blue[{lbl}] ❄️")
            else:
                st.markdown(f"### :green[{lbl}] ✅")

        st.markdown("---")
        
        df_chart = pd.DataFrame(st.session_state["data_log"])
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.caption("Grafik Suhu Real-time")
            if not df_chart.empty:
                fig_temp = px.line(df_chart, x='timestamp', y='temperature', markers=True)
                fig_temp.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_temp, width="stretch") # Fix width
            
        with col_chart2:
            st.caption("Korelasi Temp vs Hum")
            if not df_chart.empty:
                color_map = {"panas": "red", "normal": "green", "dingin": "blue", "unknown": "gray"}
                fig_scatter = px.scatter(
                    df_chart, x='temperature', y='humidity', 
                    color='predicted_label', color_discrete_map=color_map
                )
                fig_scatter.update_layout(margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_scatter, width="stretch") # Fix width

        with st.expander("Lihat Data Log Lengkap"):
            st.dataframe(df_chart.iloc[::-1], width="stretch") # Fix width
            
    else:
        st.info("Menunggu data masuk dari sensor...")


update_dashboard()