#!/usr/bin/env bash
# AirCue Raspberry Pi Installation & Setup Script
set -e

echo "=== Installing AirCue on Raspberry Pi ==="
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv mosquitto mosquitto-clients alsa-utils

echo "=== Configuring Virtual Environment ==="
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[tts]"

echo "=== Building Audio Clips ==="
aircue clips build --backend beep

echo "=== Enabling Mosquitto & AirCue Systemd Service ==="
sudo cp deploy/mosquitto.conf /etc/mosquitto/conf.d/aircue.conf
sudo systemctl restart mosquitto
sudo cp deploy/aircue.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aircue.service

echo "=== AirCue installation completed successfully! ==="
