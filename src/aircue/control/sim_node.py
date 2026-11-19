"""Simulated outdoor ESP32 node publishing realistic telemetry over MQTT."""
from __future__ import annotations

import time
from rich.console import Console
from aircue.transport.mqtt import MqttClient


def run_simulated_node(
    site: str = "indore_school_01",
    broker: str = "localhost",
    port: int = 1883,
    interval_seconds: float = 2.0,
    count: int = 0,
) -> None:
    """Publish simulated sensor telemetry (PM2.5, PM10, temperature, humidity) over MQTT."""
    console = Console()
    client = MqttClient(broker=broker, port=port, client_id=f"sim_node_{site}")
    client.connect()

    topic = f"aircue/{site}/telemetry"
    console.print(f"[green]Simulated Node started for site '[cyan]{site}[/cyan]'. Publishing to '{topic}'...[/green]")

    sent = 0
    # Simulate a rising and falling pollution curve
    base_pm = 35.0
    try:
        while True:
            sent += 1
            # Wave pattern
            pm25 = round(base_pm + 25.0 * (1.0 + (sent % 20) / 10.0), 1)
            pm10 = round(pm25 * 1.7, 1)
            temp = 28.5
            humidity = 58.0

            payload = {
                "ts": time.time(),
                "site": site,
                "pm2_5": pm25,
                "pm10": pm10,
                "temperature": temp,
                "humidity": humidity,
            }

            client.publish(topic, payload)
            console.print(f"[{sent}] Published telemetry: PM2.5={pm25} µg/m³, PM10={pm10} µg/m³")

            if count > 0 and sent >= count:
                break
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        console.print("\n[yellow]Simulated node stopped by user.[/yellow]")
    finally:
        client.disconnect()
