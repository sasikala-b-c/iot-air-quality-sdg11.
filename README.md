# IoT Air Quality Monitoring (SDG 11)

Minimal setup: MQTT broker + Streamlit dashboard that subscribes directly to MQTT + optional simulator. No API/DB.

- Device: ESP32 + DHT22 + MQ-135 (optional; use simulator if no hardware)
- Transport: MQTT (local Mosquitto via Docker)
- Dashboard: Streamlit subscribes to `iot/air/<device_id>/telemetry`
- Simulator: Python publisher of synthetic data

## Quick Start

1) Start MQTT broker (Docker):

```bash
# in repo root
docker compose up -d
```

2) Start simulator (optional):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
pip install -r simulator/requirements.txt
python simulator/publisher.py
```

3) Start dashboard:

```bash
# with the same venv active
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

Open http://localhost:8501. In the sidebar set Device ID (default `esp32-sim-1`).

## MQTT Topic and Payload

- Topic: `iot/air/<device_id>/telemetry`
- JSON payload example:

```json
{
  "device_id": "esp32-sim-1",
  "timestamp": "2025-01-01T12:00:00Z",
  "temperature_c": 28.5,
  "humidity_pct": 62.1,
  "aqi_proxy": 145.0
}
```

## Repo Structure

```
.
├─ dashboard/         # Streamlit (subscribes to MQTT)
├─ simulator/         # MQTT publisher (synthetic data)
├─ firmware/          # ESP32 sketch example
├─ mosquitto/         # Broker config
├─ docker-compose.yml # Start Mosquitto locally
├─ README.md
└─ LICENSE
```

## SDG 11

This project supports local air quality awareness for sustainable cities and communities.

MIT Licensed.
# iot-air-quality-sdg11.
