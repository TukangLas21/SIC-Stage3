#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h> // Install library ArduinoJson by Benoit Blanchon

// --- KONFIGURASI WIFI & MQTT ---
#define SSID "janganbukayoutube"
#define PASSWORD "beneranjanganbukaya"
#define MQTT_SERVER "broker.hivemq.com" // Bisa pakai broker publik atau lokal
#define MQTT_PORT 1883
#define PUBLISH_TOPIC "SamsungPintar/iot/sensor/data"
#define SUBSCRIBE_TOPIC "SamsungPintar/iot/output"

// --- KONFIGURASI PIN ---
#define DHTPIN 4      // Pin Data DHT11
#define DHTTYPE DHT11
#define BUZZER_PIN 2  // Pin Buzzer/LED

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;
PubSubClient client(espClient);

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

// Fungsi Callback untuk menerima pesan MQTT
void callback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // Logika Trigger Output
  if (String(topic) == "iot/output") {
    if (message == "BUZZER_ON") {
      digitalWrite(BUZZER_PIN, HIGH);
      Serial.println(">> ALARM NYALA!");
    } else if (message == "BUZZER_OFF") {
      digitalWrite(BUZZER_PIN, LOW);
      Serial.println(">> ALARM MATI");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Subscribe ke topik output untuk menerima perintah
      client.subscribe(SUBSCRIBE_TOPIC);
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
  dht.begin();
  setup_wifi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
  client.setCallback(callback);
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

    // Buat JSON Payload
    // Format: {"temp": 31.5, "hum": 65.2}
    StaticJsonDocument<200> doc;
    doc["temperature"] = t;
    doc["humidity"] = h;
    char buffer[256];
    serializeJson(doc, buffer);

    client.publish(PUBLISH_TOPIC, buffer);
    Serial.print("Published: ");
    Serial.println(buffer);
  }
}