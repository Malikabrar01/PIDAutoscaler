import requests
import time
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")


class PIDController:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        self.integral = 0
        self.prev_error = 0

    def compute(self, current_value, dt):
        error = current_value - self.setpoint

        p = self.kp * error

        self.integral += error * dt
        max_integral = 100
        self.integral = max(-max_integral, min(max_integral, self.integral))
        i = self.ki * self.integral

        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        d = self.kd * derivative

        self.prev_error = error

        output = p + i + d
        return output


def get_current_load():
    response = requests.get("http://localhost:8000/metrics")
    data = response.json()
    return data["cpu_usage_percent"]


def predict_next_load(history, steps_ahead=5):
    if len(history) < 15:
        return None
    try:
        model = ARIMA(history, order=(2, 1, 2))
        fitted = model.fit()
        forecast = fitted.forecast(steps=steps_ahead)
        return forecast[-1]
    except Exception:
        return None


def scale_decision(pid_output):
    if pid_output > 5:
        instances_to_add = round(pid_output / 10)
        return f"SCALE UP by {instances_to_add} instance(s)"
    elif pid_output < -5:
        instances_to_remove = round(abs(pid_output) / 10)
        return f"SCALE DOWN by {instances_to_remove} instance(s)"
    else:
        return "NO CHANGE"


if __name__ == "__main__":
    pid = PIDController(kp=1.2, ki=0.05, kd=0.3, setpoint=60)
    load_history = []
    MAX_HISTORY = 60
    dt = 2

    print("Starting Predictive PID Autoscaler...")
    print(f"Target CPU usage: {pid.setpoint}%\n")

    while True:
        current_load = get_current_load()
        load_history.append(current_load)
        if len(load_history) > MAX_HISTORY:
            load_history.pop(0)

        predicted_load = predict_next_load(load_history)

        # Use predicted load if available, otherwise fall back to current load
        input_value = predicted_load if predicted_load is not None else current_load

        output = pid.compute(input_value, dt)
        decision = scale_decision(output)

        if predicted_load is not None:
            print(f"Current: {current_load:.2f}% | Predicted: {predicted_load:.2f}% | PID output: {output:.2f} | Decision: {decision}")
        else:
            print(f"Current: {current_load:.2f}% | Collecting data... | Decision: {decision}")

        time.sleep(dt)



