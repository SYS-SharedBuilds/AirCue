#ifndef CONFIG_H
#define CONFIG_H

// Wi-Fi Configuration
#define WIFI_SSID "YOUR_SCHOOL_WIFI"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// MQTT Broker Configuration
#define MQTT_BROKER "192.168.1.100" // Raspberry Pi IP
#define MQTT_PORT 1883
#define SITE_ID "indore_school_01"

// Hardware Pin Definitions
#define PIN_PMS_RX 16
#define PIN_PMS_TX 17
#define PIN_BUTTON_SNOOZE 4
#define PIN_LED_RED 21
#define PIN_LED_GREEN 22
#define PIN_LED_BLUE 23

#endif
