# Keteranan
- dataset_finpro.csv: Dataset yang digunakan untuk pelatihan model klasifikasi suhu.
- SamsungPintar_SIC.ipynb: Notebook Jupyter yang berisi kode untuk pelatihan model klasifikasi suhu menggunakan dataset_finpro.csv.
- dashboard.py: Aplikasi dashboard streamlit.
- data_gathering.py: Skrip Python untuk mengumpulkan data sensor melalui MQTT dan menyimpan ke file CSV.
- main.cpp: Kode arduino yang menginclude header file implementasi. Uncomment include yang diperlukan.
- data_gathering.h: Header file implementasi pengumpulan data sensor melalui MQTT.
- deployment.h: Header file implementasi deployment model klasifikasi suhu pada mikrokontroler.
- iot_temp_model_<model>.pkl: Model klasifikasi suhu yang telah dilatih dan disimpan dalam format pickle.


# Menjalankan streamlit dashboard
1. Pastikan semua dependensi telah terinstall, termasuk streamlit, pandas, scikit-learn, joblib, paho-mqtt, plotly.
2. Jalankan perintah berikut di terminal:
   ```
   streamlit run dashboard.py
   ```

# Cara upload model ke mikrokontroler
1. Buka file `main.cpp` pada Arduino IDE.
2. Uncomment baris `#include "deployment.h"` dan comment baris `#include "data_gathering.h"` (atau sebaliknya).
3. Pastikan file `deployment.h` sudah berisi model yang ingin diupload.
4. Upload kode ke mikrokontroler menggunakan platformio (pastikan platformio sudah terinstall dan direktori project di folder `streamlit-esp32`):
    ```
    pio run --target upload
    ```