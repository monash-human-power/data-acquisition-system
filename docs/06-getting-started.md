# 6. Getting started, tech stack, and running

Extended “production-style” guide. For the short repo intro and contributors, see the root [`README.md`](../README.md).

## Project title

**Monash Human Power — Data Acquisition System**

## Description

Telemetry stack for a human-powered vehicle: ESP32 and Raspberry Pi devices publish sensor data over MQTT; tools record, replay, and post-process runs. An optional radio bridge links MQTT between bike and chase car.

## Features

- **MQTT logging** — Subscribe and persist to SQLite (`DAS/das/V3_mqtt_recorder.py`).
- **Playback and simulation** — V2/V3 playback and fake wireless modules.
- **Wireless modules** — MicroPython on ESP32 (`wireless_modules/`) with JSON on `/v3/wireless_module/{id}/...`.
- **Wired modules** — ESP32 C++ I2C sensors via `SensorBase` (`wired_module/`), topics `sensor/{hex}`.
- **ANT+** — Node bridge from USB ANT+ to MQTT (`ant_plus_sensor/`).
- **Radio MQTT bridge** — C++ over ZetaRF (`Bridge/`).
- **Crash alerts** — MQTT-driven Slack notifications (`crash_alert/`).
- **Post-processing** — Spreadsheet merge / interpolation (`utils/turps.py`).

## Tech stack

- Python 3.7+ (Poetry), Paho MQTT, internal `mhp` package from `monash-human-power/common`.
- C++ (CMake): Paho MQTT C++, ZetaRF, RF24 on Raspberry Pi.
- MicroPython: `umqtt`, `uasyncio`.
- Node.js: MQTT + ANT+ (`ant_plus_sensor`).

## Prerequisites

- Git with submodules (`Bridge`, `wireless_modules` libraries — see [`.gitmodules`](../.gitmodules)).
- For **DAS**: [Poetry](https://python-poetry.org/) and SSH access to GitHub for the `mhp` dependency.
- For **Bridge**: follow [`Bridge/README.md`](../Bridge/README.md) (wiringpi, Paho MQTT C, RF24, CMake).

## Installation (summary)

Clone with submodules:

```bash
git clone --recurse-submodules https://github.com/monash-human-power/data-acquisition-system.git
cd data-acquisition-system
```

### DAS (Python tools)

```bash
cd DAS
poetry install
```

### Crash alert

```bash
cd crash_alert
cp .env.example .env   # configure SLACK_WEBHOOK, etc.
poetry install
poetry run python main_crash_alert.py
```

### Bridge

Build and run per [`Bridge/README.md`](../Bridge/README.md) (e.g. `./build/ZetaBridge`).

### ANT+ logger

Per [`ant_plus_sensor/README.md`](../ant_plus_sensor/README.md) (Node, udev, optional `sudo`).

## How to run (examples)

- **Record MQTT** (from `DAS/`):

  ```bash
  poetry run python -m das.V3_mqtt_recorder /v3/# -v
  ```

- **Wireless module**: flash MicroPython, add `config.py` on device; see [`wireless_modules/README.md`](../wireless_modules/README.md).

- **Bridge**: run the built binary on two Pis as in [`Bridge/README.md`](../Bridge/README.md).

## Project structure (brief)

| Directory | Purpose |
|-----------|---------|
| `DAS/` | Recorder, playback, fake module, log→Excel |
| `Bridge/` | MQTT ↔ ZetaRF radio bridge |
| `wireless_modules/` | MicroPython wireless stack |
| `wireless_modules_py/` | Python wireless module |
| `wired_module/` | ESP32 Arduino-style firmware |
| `ant_plus_sensor/` | ANT+ to MQTT |
| `crash_alert/` | Crash detection → Slack |
| `utils/` | Log interpolation (`turps.py`) |
| `services/` | systemd unit examples |
| `docs/` | Engineering handover docs |

## Future improvements

- Configuration for Bridge (broker, banned topics) without source edits.
- Non-blocking MQTT publish queue in Bridge.
- Automated tests for DAS and firmware smoke builds.
- Align or gateway between wired (`sensor/xx`) and `/v3/...` topic layouts.

## Further reading

- [`DAS/README.md`](../DAS/README.md) — CLI flags for recorder/playback.
- [`Bridge/README.md`](../Bridge/README.md) — build and protocol overview.
- [`services/README.md`](../services/README.md) — systemd deployment.
