import requests
import time

# Simple threshold-based autoscaler (mimics default Kubernetes HPA behavior)

TARGET = 60  # target CPU usage %
UPPER_THRESHOLD = 80  # scale up if load exceeds this
LOWER_THRESHOLD = 40  # scale down if load drops below this

def get_current_load():
    response = requests.get("http://localhost:8000/metrics")
    data = response.json()
    return data["cpu_usage_percent"]

def naive_decision(current_load):
    """
    Dumb logic: no memory, no prediction, just a fixed threshold check.
    This is exactly how many real-world autoscalers work by default.
    """
    if current_load > UPPER_THRESHOLD:
        return "SCALE UP by 1 instance"
    elif current_load < LOWER_THRESHOLD:
        return "SCALE DOWN by 1 instance"
    else:
        return "NO CHANGE"

if __name__ == "__main__":
    dt = 2

    print("Starting Naive Threshold Autoscaler...")
    print(f"Scale up if load > {UPPER_THRESHOLD}%, scale down if load < {LOWER_THRESHOLD}%\n")

    while True:
        current_load = get_current_load()
        decision = naive_decision(current_load)

        print(f"Current load: {current_load:.2f}% | Decision: {decision}")

        time.sleep(dt)
