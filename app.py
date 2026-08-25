from fastapi import FastAPI
import random
import time
import math

app = FastAPI()

# Simulated starting load (percentage, like CPU usage)
current_load = 30.0

# Tracks how long the server has been "running" — used to create wave patterns
start_time = time.time()

@app.get("/metrics")
def get_metrics():
    """
    Returns simulated CPU load as a percentage.
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

    return {
        "cpu_usage_percent": round(current_load, 2),
        "timestamp": elapsed
    }

@app.get("/")
def root():
    return {"message": "PIDAutoscaler load simulator is running"}
