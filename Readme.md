# PIDAutoscaler

PID-controller-based autoscaler with ML-driven load prediction to proactively 
scale infrastructure and reduce oscillation vs. threshold-based autoscaling.

## What it does

Replaces naive threshold-based autoscaling (like default Kubernetes HPA) with 
a PID control loop, reducing overshoot and oscillation. The system is monitored 
end-to-end with Prometheus and Grafana, and will be enhanced with a time-series 
prediction layer (ARIMA) to forecast load ahead of time, enabling proactive 
scaling before traffic spikes hit.

## Live monitoring dashboard

![Grafana dashboard showing live simulated load](Resources/pidautoscaler-graph.png)

*Real-time CPU load simulation scraped by Prometheus and visualized in Grafana, 
updating every 5 seconds.*

## Architecture

- **app.py** — simulates a server's fluctuating CPU load (sine wave + noise + 
  occasional spikes), exposed via both a JSON endpoint and a Prometheus-format 
  metrics endpoint
- **controller.py** — PID controller that polls load and computes scaling 
  decisions using proportional, integral, and derivative terms
- **naive_controller.py** — simple threshold-based baseline (mimics default 
  Kubernetes HPA behavior) used for comparison against the PID approach
- **Prometheus** — scrapes simulated load metrics every 5 seconds
- **Grafana** — visualizes live and historical load data

## Key engineering decisions

- **Anti-windup clamping**: bounded the PID integral term to prevent unbounded 
  growth during sustained load deviation, which otherwise caused runaway 
  scaling recommendations
- **Corrected error direction**: standard PID convention (`setpoint - current`) 
  assumes driving a value down to a target; autoscaling needs the opposite 
  (scale up when load exceeds target), so the error term was inverted to 
  `current - setpoint` to match the domain
- **Fixed stale metrics bug**: the Prometheus metrics endpoint initially read a 
  cached `current_load` value instead of triggering fresh computation on each 
  scrape, causing a flat/stale graph — refactored both endpoints to share a 
  single `calculate_load()` function

## Tech stack

Python, FastAPI, Prometheus, Grafana, Docker

## Status

Work in progress — PID controller, naive baseline, and monitoring pipeline are 
complete. Next: ARIMA-based load prediction integrated into the PID setpoint 
for proactive scaling.
