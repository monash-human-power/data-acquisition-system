# 1. Project overview

## What the project does

A **bike-mounted data acquisition system**: microcontrollers and Raspberry Pis collect sensor data, publish it over **MQTT** (topics such as `/v3/...`, `boost/#`), log and replay sessions, optionally **bridge MQTT over radio** between bike and chase car, integrate **ANT+** via Node.js, and send **crash notifications** (e.g. Slack).

## Core problem it solves

The team needs **time-synchronized, multi-sensor telemetry** from a human-powered vehicle during development and runs, with **logging**, **test harnesses**, and **connectivity** between separated networks (e.g. chase car vs bike) without relying on a single shared LAN.

## Key features (evidence in code)

| Area | Location / mechanism |
|------|----------------------|
| MQTT logging to SQLite | `DAS/das/V3_mqtt_recorder.py` — `mqtt_logger.Recorder` → `MQTT_log.db` |
| Playback / simulation | `V3_mqtt_playback.py`, `V3_fake_module.py`, `V2_mqtt_playback.py` |
| Excel pipeline | `log_2_excel.py` (see `DAS/README.md`) |
| Post-processing | `utils/turps.py` — interpolate Excel → merged CSV |
| Radio MQTT bridge | `Bridge/` — subscribe `#`, filter, pack frames, `ZetaRfRadio` |
| ESP32 wired sensors | `wired_module/wired_module_arduino/`, `wired_module/vm code 2.1/` — `SensorBase`, topics `sensor/%02x` |
| Wireless modules (MicroPython) | `wireless_modules/` — `WirelessModule`, `umqtt`, `v3/start`, `/v3/wireless_module/{id}/...` |
| Python wireless variant | `wireless_modules_py/` — `mhp` topic helpers |
| ANT+ → MQTT | `ant_plus_sensor/ant_plus_logger.js` |
| Crash alerts | `crash_alert/` — MQTT + Slack webhook |
| systemd | `services/*.service` |

## Target users

**Monash Human Power** (student racing team): engineers operating Pis and ESP32 in the field, and maintainers of logging/replay tooling. Inferred from the root `README.md` and “MHP” naming in `services/`.
