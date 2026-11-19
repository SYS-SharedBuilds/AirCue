# AirCue ESP32 Outdoor Sensor Node Firmware

This directory contains the PlatformIO Arduino firmware for the outdoor ESP32 node.

## Quickstart
1. Copy `include/config.example.h` to `include/config.h`.
2. Configure Wi-Fi credentials and Raspberry Pi MQTT broker IP address.
3. Build and upload using PlatformIO:
   ```bash
   pio run -t upload
   ```
4. Open serial monitor at 115200 baud:
   ```bash
   pio device monitor
   ```
