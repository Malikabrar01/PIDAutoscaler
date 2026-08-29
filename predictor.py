import requests
import time
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

# Store recent load history for the model to learn from
load_history = []
MAX_HISTORY = 60  # keep last 60 readings (~2 minutes at 2s intervals)


def get_current_load():
    """Poll the simulator's /metrics endpoint"""
    response = requests.get("http://localhost:8000/metrics")
    data = response.json()
    return data["cpu_usage_percent"]


def predict_next_load(history, steps_ahead=5):
    """
    Fit an ARIMA model on recent history and forecast future load.
    steps_ahead: how many future points to predict (each point = one polling interval)
    """
    if len(history) < 15:
        # Not enough data yet to fit a meaningful model
        return None

    try:
        model = ARIMA(history, order=(2, 1, 2))
        fitted = model.fit()
        forecast = fitted.forecast(steps=steps_ahead)
        return forecast[-1]  # return the furthest-out prediction
    except Exception as e:
        print(f"Prediction failed: {e}")
        return None


if __name__ == "__main__":
    dt = 2  # seconds between polls

    print("Starting ARIMA Load Predictor...")
    print("Collecting initial data before predictions begin...\n")

    while True:
        current_load = get_current_load()
        load_history.append(current_load)

        # Keep history bounded
        if len(load_history) > MAX_HISTORY:
            load_history.pop(0)

        prediction = predict_next_load(load_history)

        if prediction is not None:
            print(f"Current: {current_load:.2f}% | Predicted (in ~10s): {prediction:.2f}%")
        else:
            print(f"Current: {current_load:.2f}% | Collecting data... ({len(load_history)}/15 minimum)")

        time.sleep(dt)