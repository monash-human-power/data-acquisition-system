# 3. Current implementation status

## Fully implemented (code present and intended paths exist)

- DAS tooling: MQTT recorder (`V3_mqtt_recorder.py`), V2/V3 playback, fake module, log utilities under `DAS/das/`.
- Bridge: full C++ pipeline (`Bridge/src/`) — MQTT client, framing, ZetaRF radio.
- Wireless MicroPython: MQTT client, `WirelessModule`, sensor drivers under `wireless_modules/sensors/`.
- Crash alert: Slack path when MQTT payload has `"value": true` (`main_crash_alert.py`, `crash_alert.py`).
- ANT+ logger: Node pipeline (`ant_plus_logger.js`).
- systemd examples: `services/*.service`.

## Partial, incomplete, or risky


| Issue                                                  | Evidence                                                                                                          |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `**vm code 2.1` firmware may not compile**             | `wired_module/vm code 2.1/src/main.cpp`: nested `void loop()` inside `void loop()` — invalid C++.                 |
| `**wired_module_arduino` never runs main sensor loop** | `setup()` ends with `while (true) { Serial.println("ESP32 is alive!"); }` — `loop()` unreachable for normal flow. |
| **I2C address clash risk**                             | `wired_module_arduino/src/main.cpp`: `MpuSensor` and `ICM42670` both at `0x68` in the same `sensors` list.        |
| `**vm code 2.1` setup churn**                          | Duplicate WiFi connection logic; `Serial.begin` ordering vs connection.                                           |
| **Crash alert docs vs code**                           | `crash_alert/README.md` describes 10s cooldown; CLI default `--cooldown` is **120** in `main_crash_alert.py`.     |
| **SNS not wired**                                      | `SnsMessageSender` imported in `crash_alert.py` but not added to `self.apis` in `CrashAlert.__init__`.            |
| **No DAS test suite**                                  | `pytest` in `pyproject.toml` but no `test_*.py` files under `DAS/`.                                               |
| **Bridge configuration**                               | Broker address and banned topics require source edits (`Bridge/README.md`, `bridge.cpp`).                         |


## TODOs / FIXMEs in repo (non-exhaustive)

- `Bridge/src/bridge.cpp` — flexible banned-topic list vs hardcoded.
- `Bridge/src/mqtt.cpp` — publish queue vs blocking wait.
- `Bridge/src/nrf24.cpp` — SPI speed testing.
- `wireless_modules/wireless_module.py` — FIXME: restart tasks vs full reset.
- `DAS/das/V3_fake_module.py`, `log_2_excel.py`, `wireless_modules/sensors/mpu_sensor.py` — various TODOs.

## Technical debt (visible)

- Including `DPS368.cpp` from `main.cpp` instead of a normal compile unit.
- Topic split: `**sensor/xx`** (wired) vs `**/v3/wireless_module/...**` (wireless) — integration overhead for consumers.
- Full **MCU reset** on MicroPython asyncio errors (`wireless_module.py`).

