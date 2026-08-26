import requests
import time

class PIDController:
    def __init__(self, kp, ki, kd, setpoint):
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        self.setpoint = setpoint  # target CPU usage %

        self.integral = 0
        self.prev_error = 0

    def compute(self, current_value, dt):
        error = current_value - self.setpoint



        p = self.kp * error

        # Integral term with anti-windup clamping
        self.integral += error * dt
        max_integral = 100  # clamp to prevent windup
        self.integral = max(-max_integral, min(max_integral, self.integral))
        i = self.ki * self.integral

        # Derivative term (rate of change of error)
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        d = self.kd * derivative

        self.prev_error = error

        output = p + i + d
        return output


def get_current_load():
    """Poll the simulator's /metrics endpoint"""
    response = requests.get("http://localhost:8000/metrics")
    data = response.json()
    return data["cpu_usage_percent"]


def scale_decision(pid_output):
    """
    Convert PID output into a scaling action.
    Positive output = load is above target -> scale up
    Negative output = load is below target -> scale down
    """
    if pid_output > 5:
        instances_to_add = round(pid_output / 10)
        return f"SCALE UP by {instances_to_add} instance(s)"
    elif pid_output < -5:
        instances_to_remove = round(abs(pid_output) / 10)
        return f"SCALE DOWN by {instances_to_remove} instance(s)"
    else:
        return "NO CHANGE"


if __name__ == "__main__":
    # Target: keep CPU usage at 60%
    pid = PIDController(kp=1.2, ki=0.05, kd=0.3, setpoint=60)

    dt = 2  # seconds between checks

    print("Starting PID Autoscaler Controller...")
    print(f"Target CPU usage: {pid.setpoint}%\n")

    while True:
        current_load = get_current_load()
        output = pid.compute(current_load, dt)
        decision = scale_decision(output)

        print(f"Current load: {current_load:.2f}% | PID output: {output:.2f} | Decision: {decision}")

        time.sleep(dt)
