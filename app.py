from fastapi import FastAPI, Response
from prometheus_client import Gauge, generate_latest
import random
import time
import math

app = FastAPI()

cpu_gauge = Gauge('simulated_cpu_usage_percent', 'Simulated CPU usage percentage')

# Simulated starting load (percentage, like CPU usage)
current_load = 30.0

# Tracks how long the server has been "running" — used to create wave patterns
start_time = time.time()


def calculate_load():
    """
    Shared logic to compute simulated load. Called by both /metrics and
    /prometheus-metrics so the value updates regardless of which endpoint
    is being polled.

    Combines three things to make it realistic:
    1. A slow wave (simulates daily traffic patterns rising and falling)
    2. Random noise (simulates natural fluctuation)
    3. Occasional random spikes (simulates sudden traffic bursts)
    """
    global current_load

    elapsed = time.time() - start_time

    # 1. Base wave: oscillates slowly between low and high load
    wave = 50 + 30 * math.sin(elapsed / 20)

    # 2. Random noise: small random jitter every call
    noise = random.uniform(-5, 5)

    # 3. Occasional spike: 5% chance of a sudden traffic burst
    spike = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 40]) if random.random() < 0.05 else 0

    current_load = max(0, min(100, wave + noise + spike))
    return current_load


@app.get("/metrics")
def get_metrics():
    """Returns simulated CPU load as a percentage (JSON format)."""
    load = calculate_load()
    elapsed = time.time() - start_time

    return {
        "cpu_usage_percent": round(load, 2),
        "timestamp": elapsed
    }


@app.get("/prometheus-metrics")
def prometheus_metrics():
    """Returns simulated CPU load in Prometheus scrape format."""
    load = calculate_load()
    cpu_gauge.set(load)
    return Response(generate_latest(), media_type="text/plain")


@app.get("/")
def root():
    return {"message": "PIDAutoscaler load simulator is running"}
