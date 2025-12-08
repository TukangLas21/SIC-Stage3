#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "realme XT";
const char* password = "gratis123";
const char* mqtt_server = "broker.hivemq.com";

// topic untuk kirim data sensor ke Colab
const char* sensorTopic = "iot/class/session5/sensor";

// topic untuk menerima output ML dari Colab
const char* outputTopic = "iot/class/session5/output";

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (int i=0; i<length; i++) msg += (char)payload[i];

  Serial.print("Output from ML: ");
  Serial.println(msg);

  if (msg.indexOf("ALERT") != -1) {
    Serial.println("🔥 BUZZER ON! (ML detected PANAS)");
    digitalWrite(2, HIGH);
  } else {
    digitalWrite(2, LOW);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect("esp32client12345")) {
      Serial.println("connected!");
      client.subscribe(outputTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void setup() {
  pinMode(2, OUTPUT);
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("WiFi Connected!");

  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  reconnect();
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) return;

  // bentuk data JSON yang sesuai dengan Python ML
  String jsonData = "{\"temp\": " + String(temp, 2) + ", \"hum\": " + String(hum, 2) + "}";

  client.publish(sensorTopic, jsonData.c_str());
  Serial.println("Published: " + jsonData);

  delay(2000); // publish tiap 2 detik
}
