import streamlit as st
import pandas as pd
import time
import plotly.express as px
import os

# Konfigurasi Halaman
st.set_page_config(
    page_title="Realtime IoT Dashboard",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ IoT Sensor Monitoring & ML Prediction")

# Lokasi file CSV log
CSV_FILE = "sensor_log.csv"

# Placeholder untuk konten agar bisa auto-refresh
placeholder = st.empty()

while True:
    with placeholder.container():
        # Cek apakah file CSV sudah ada
        if not os.path.exists(CSV_FILE):
            st.warning("Menunggu data... Pastikan script Controller.py berjalan.")
            time.sleep(2)
            continue
            
        # Baca data CSV
        try:
            df = pd.read_csv(CSV_FILE)
            
            # Ambil data terakhir
            if not df.empty:
                last_data = df.iloc[-1]
                
                # --- METRICS SECTION ---
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Temperature", 
                        value=f"{last_data['temperature']} °C",
                        delta_color="inverse"
                    )
                    
                with col2:
                    st.metric(
                        label="Humidity", 
                        value=f"{last_data['humidity']} %"
                    )
                    
                with col3:
                    status = last_data['predicted_label']
                    color = "red" if status == "Panas" else "green"
                    st.markdown(f"### Status: :{color}[{status}]")
                    if status == "Panas":
                        st.error("⚠️ PERINGATAN: SUHU TINGGI! BUZZER ON")
                    else:
                        st.success("✅ Kondisi Normal")

                # --- CHARTS SECTION ---
                st.markdown("---")
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.subheader("Grafik Suhu Real-time")
                    fig_temp = px.line(df, x='timestamp', y='temperature', title='Temperature History', markers=True)
                    st.plotly_chart(fig_temp, use_container_width=True)
                    
                with chart_col2:
                    st.subheader("Sebaran Data (Scatter)")
                    fig_scatter = px.scatter(df, x='temperature', y='humidity', color='predicted_label', 
                                           title='Temp vs Hum Correlation', color_discrete_map={"Panas": "red", "Normal": "green"})
                    st.plotly_chart(fig_scatter, use_container_width=True)

                # --- DATA TABLE ---
                with st.expander("Lihat Data Log Lengkap"):
                    st.dataframe(df.sort_index(ascending=False)) # Tampilkan data terbaru di atas
            
            else:
                st.info("File CSV kosong.")

        except Exception as e:
            st.error(f"Error reading CSV: {e}")

        # Auto refresh setiap 2 detik
        time.sleep(2)