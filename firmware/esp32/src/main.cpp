#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.example.h"

// If local config.h exists, include it
#if __has_include("config.h")
#include "config.h"
#endif

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void connectWiFi() {
    Serial.print("Connecting to Wi-Fi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWi-Fi Connected.");
    } else {
        Serial.println("\nWi-Fi timeout, continuing in offline fallback mode.");
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("AirCue Outdoor Node Firmware Initializing...");
    pinMode(PIN_BUTTON_SNOOZE, INPUT_PULLUP);
    pinMode(PIN_LED_RED, OUTPUT);
    pinMode(PIN_LED_GREEN, OUTPUT);
    pinMode(PIN_LED_BLUE, OUTPUT);

    connectWiFi();
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
    if (WiFi.status() == WL_CONNECTED && !mqttClient.connected()) {
        mqttClient.connect(SITE_ID);
    }
    mqttClient.loop();

    // Telemetry read simulation loop (in production, UART PMS5003 packet parser)
    static unsigned long lastMsg = 0;
    if (millis() - lastMsg > 10000) {
        lastMsg = millis();
        JsonDocument doc;
        doc["ts"] = millis() / 1000;
        doc["site"] = SITE_ID;
        doc["pm2_5"] = 42.5;
        doc["pm10"] = 85.0;
        doc["temperature"] = 28.0;
        doc["humidity"] = 55.0;

        char buffer[256];
        serializeJson(doc, buffer);
        mqttClient.publish("aircue/" SITE_ID "/telemetry", buffer);
    }
    delay(100);
}
