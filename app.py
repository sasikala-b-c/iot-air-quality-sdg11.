import os
import time
import json
from collections import deque
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
DEFAULT_DEVICE = os.getenv("DEVICE_ID", "esp32-sim-1")

st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("IoT Air Quality Monitoring - SDG 11")

# Sidebar controls
with st.sidebar:
    broker_host = st.text_input("MQTT Host", MQTT_BROKER_HOST)
    broker_port = st.number_input("MQTT Port", value=MQTT_BROKER_PORT, step=1)
    device_id = st.text_input("Device ID", DEFAULT_DEVICE)
    max_points = st.slider("History size", min_value=50, max_value=2000, value=300, step=50)
    refresh_sec = st.slider("Refresh (sec)", 1, 10, 2)

topic = f"iot/air/{device_id}/telemetry"

# Session state for data buffer and MQTT client
if "buffer" not in st.session_state:
    st.session_state["buffer"] = deque(maxlen=1000)
if "mqtt_client" not in st.session_state:
    st.session_state["mqtt_client"] = None


def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(topic, qos=0)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        ts = payload.get("timestamp") or datetime.utcnow().isoformat() + "Z"
        st.session_state["buffer"].append(
            {
                "timestamp": ts,
                "temperature_c": payload.get("temperature_c"),
                "humidity_pct": payload.get("humidity_pct"),
                "aqi_proxy": payload.get("aqi_proxy"),
            }
        )
    except Exception:
        pass


def ensure_mqtt():
    # Recreate client if not exists or connection params changed
    need_new = False
    c = st.session_state.get("mqtt_client")
    if c is None:
        need_new = True
    else:
        # no simple way to check host change; recreate if topic changes
        try:
            c.unsubscribe("#")
        except Exception:
            pass
        try:
            c.disconnect()
        except Exception:
            pass
        need_new = True

    if need_new:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker_host, int(broker_port), keepalive=60)
        client.loop_start()
        st.session_state["mqtt_client"] = client


ensure_mqtt()

cols = st.columns(3)
chart_placeholder = st.empty()

# Auto-refresh
st.experimental_set_query_params()

buf = list(st.session_state["buffer"])[-max_points:]
if buf:
    df = pd.DataFrame(buf)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp")
    last = df.iloc[-1]
    with cols[0]:
        st.metric("Temperature (°C)", f"{last.get('temperature_c', float('nan'))}")
    with cols[1]:
        st.metric("Humidity (%)", f"{last.get('humidity_pct', float('nan'))}")
    with cols[2]:
        st.metric("AQI Proxy", f"{last.get('aqi_proxy', float('nan'))}")

    chart_placeholder.line_chart(
        df.set_index("timestamp")[
            [c for c in ["temperature_c", "humidity_pct", "aqi_proxy"] if c in df.columns]
        ]
    )
else:
    st.info("No data yet. Start the simulator or device.")

# Trigger auto refresh
st.write(f"Auto-refreshing every {refresh_sec}s…")
time.sleep(refresh_sec)
st.rerun()
