#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h> // Install library ArduinoJson by Benoit Blanchon
#include "iot_temp_model_svm.h"

// --- KONFIGURASI WIFI & MQTT ---
#define SSID "janganbukayoutube"
#define PASSWORD "beneranjanganbukaya"
#define MQTT_SERVER "broker.hivemq.com" // Bisa pakai broker publik atau lokal
#define MQTT_PORT 1883
#define PUBLISH_TOPIC "SamsungPintar/data"

// --- KONFIGURASI PIN ---
#define DHTPIN 4      // Pin Data DHT11
#define DHTTYPE DHT11
#define BUZZER_PIN 2  // Pin Buzzer/LED MERAH
#define YELLOW_LED_PIN 15 // LED KUNING
#define GREEN_LED_PIN 13  // LED HIJAU


DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);
Eloquent::ML::Port::SVM clf;
const char* const classes[] = {"dingin", "normal", "panas"};

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(SSID);
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  dht.begin();
  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Kirim data setiap 2 detik
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println("Gagal baca sensor DHT!");
      return;
    }

    
    // Prediksi Kelas dengan Model SVM
    float input[2] = {t, h};
    int predicted_class = clf.predict(input);
    Serial.print("Predicted class: ");
    Serial.println(classes[predicted_class]);

    // Indikasikan dengan Buzzer/LED
    if (predicted_class == 0) { // dingin
      digitalWrite(BUZZER_PIN, LOW); // Matikan buzzer
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, HIGH);
    } else if (predicted_class == 1) { // normal
      digitalWrite(BUZZER_PIN, LOW); // Matikan buzzer
      digitalWrite(YELLOW_LED_PIN, HIGH);
      digitalWrite(GREEN_LED_PIN, LOW);
    } else if (predicted_class == 2) { // panas
      digitalWrite(YELLOW_LED_PIN, LOW);
      digitalWrite(GREEN_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, HIGH); // Nyalakan buzzer
      delay(500);
      digitalWrite(BUZZER_PIN, LOW); // Matikan buzzer
    }

    // Buat JSON Payload
    // Format: {"temp": 31.5, "hum": 65.2}
    StaticJsonDocument<200> doc;
    doc["temperature"] = t;
    doc["humidity"] = h;
    doc["label"] = classes[predicted_class];
    char buffer[256];
    serializeJson(doc, buffer);

    // Publish ke MQTT
    client.publish(PUBLISH_TOPIC, buffer);
    Serial.print("Published: ");
    Serial.println(buffer);
  }
}