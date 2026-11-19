# AirCue Outdoor Hardware Specification

## 1. System Architecture: Distributed Outdoor Node to Indoor Master
To ensure long-term durability in Indian weather extremes (heat, monsoon, dust storms), AirCue separates physical environmental sensing from heavy compute/audio amplification:

```
[Outdoor Sensor Node (ESP32 + PMS5003 + BME280)]
   │ (Wi-Fi 2.4 GHz MQTT)
   ▼
[Raspberry Pi 4 Service (Indoor / Sheltered)]
   │ (Line-Out / High-Gain Audio Amp)
   ▼
[High-Decibel Weatherproof Outdoor PA Horn Speaker (Assembly Ground / Sports Field)]
```

## 2. Bill of Materials (BOM)

### A. Outdoor Sensor Node
- **Microcontroller**: ESP32 DevKit v1 (Dual-core, Wi-Fi/BLE).
- **Particulate Sensor**: Plantower PMS5003 (Laser scattering particle counter, UART interface; SPS30 as alternate).
- **Meteorological Sensor**: Bosch BME280 (Temperature, Relative Humidity, Barometric Pressure, I2C interface).
- **Visual Alert Array**: High-intensity sunlight-readable RGB LEDs with frosted diffuser lenses (Red, Yellow/Amber, Green).
- **Physical Controls**: IP67 momentary push button (Short press = 30-min snooze, Long press = mute toggle).
- **Enclosure**: IP65 UV-resistant polycarbonate junction box with a downward-ventilated Stevenson radiation shield for ambient air sampling without rain ingress.
- **Power**: 5V 2A DC mains adapter or 12V 20W Solar Panel + 12V LiFePO4 battery pack with 5V buck converter.

### B. Base Station & Audio System
- **Host Controller**: Raspberry Pi 4 Model B (2GB or 4GB) or local Linux mini-PC.
- **Audio Output**: 3.5mm line out or I2S DAC (PCM5102A).
- **Amplifier**: 30W–50W mono power amplifier with volume gain potentiometer.
- **Outdoor Speaker**: Weatherproof 30W IP66 PA horn loudspeaker mounted on assembly ground pole (90–110 dB SPL).
- **Acoustic Note**: Indoor classroom amplifiers (like MAX98357A 3W) are completely inadequate over outdoor ambient school noise (chatter, wind, nearby traffic). Minimum 30W amplified PA horn is mandatory.

## 3. Physical Placement & Breathing Height
- Mount outdoor sensor nodes 1.5 to 2.0 meters above ground level (matching the breathing zone of school students).
- Position away from local transient emission artifacts:
  - Do NOT place directly near kitchen exhaust flues, school bus parking lots, generator exhausts, or waste burning spots.
  - Position centrally adjacent to student congregation areas (morning assembly quadrangle, main playground).

## 4. Optical PM Relative Humidity Compensation
Low-cost laser particle counters overestimate particulate mass at high relative humidity (>65%) due to aerosol hygroscopic growth.
AirCue provides an optional empirical correction in `src/aircue/trigger/humidity.py`. For production deployment, co-locate the sensor node with a government CPCB CAAQMS reference station for 48 hours to calibrate empirical parameters.

## 5. Safety, Privacy & Medical Stance
- **Zero Microphone Design**: AirCue contains **no microphone** and performs no voice recording. It is strictly an announcer, eliminating student privacy concerns.
- **Non-Diagnostic Precautionary Guidance**: AirCue is designed for environmental awareness and school activity management. It is **not a certified life-safety device** or medical diagnostic instrument.
