"""Robust MQTT client wrapper using paho-mqtt."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional
import paho.mqtt.client as mqtt


class MqttClient:
    """Wrapper around paho-mqtt with auto-reconnect and structured JSON handling."""

    def __init__(
        self,
        broker: str = "localhost",
        port: int = 1883,
        client_id: str = "aircue_service",
        keepalive: int = 60,
    ) -> None:
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.keepalive = keepalive
        self.client = mqtt.Client(client_id=client_id)
        self._on_message_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        pass

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        if self._on_message_callback:
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
            except Exception:
                payload = {"raw": msg.payload.decode("utf-8", errors="ignore")}
            self._on_message_callback(msg.topic, payload)

    def set_message_handler(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        self._on_message_callback = callback

    def connect(self) -> None:
        try:
            self.client.connect(self.broker, self.port, self.keepalive)
            self.client.loop_start()
        except Exception:
            pass

    def subscribe(self, topic: str) -> None:
        try:
            self.client.subscribe(topic)
        except Exception:
            pass

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        try:
            msg_str = json.dumps(payload)
            self.client.publish(topic, msg_str)
        except Exception:
            pass

    def disconnect(self) -> None:
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception:
            pass
