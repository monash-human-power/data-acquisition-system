# 4. Product backlog

Structured by theme. Priority: High / Medium / Low. Effort: Small / Medium / Large.

## Core features


| Title                                | Description                                                                                                                  | Priority | Effort | Dependencies        |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | -------- | ------ | ------------------- |
| Fix `vm code 2.1` `main.cpp`         | Remove nested `loop()`; single `loop()` with MQTT + `sensor->send()`; clean `setup()` (`Serial.begin` first, one WiFi flow). | High     | Small  | `secrets.h`, broker |
| Fix `wired_module_arduino` `setup()` | Remove or relocate infinite `while` so `loop()` runs MQTT/sensors.                                                           | High     | Small  | Hardware validation |
| Resolve I2C `0x68` clash             | One IMU path or distinct address / bus for `MpuSensor` vs `ICM42670`.                                                        | High     | Medium | Schematic / parts   |
| Document or unify MQTT topic schemes | Wired `sensor/xx` vs `/v3/wireless_module/...` for dashboard/recorder consumers.                                             | Medium   | Medium | Product / dashboard |


## Enhancements


| Title                        | Description                                                  | Priority | Effort | Dependencies      |
| ---------------------------- | ------------------------------------------------------------ | -------- | ------ | ----------------- |
| Configurable crash module ID | `CrashAlertDriver` uses `WirelessModule.id(3)`; add CLI/env. | Medium   | Small  | `mhp` topics      |
| Multi-channel crash alerts   | Wire `SnsMessageSender` or env-driven sender list.           | Low      | Small  | AWS / credentials |
| Configurable bridge filters  | Replace substring ban list with config.                      | Medium   | Medium | Bridge deployment |
| Bridge broker CLI            | Avoid editing `mqtt.cpp` manually.                           | Medium   | Medium | CMake / args      |


## Technical improvements


| Title                               | Description                                                          | Priority | Effort | Dependencies   |
| ----------------------------------- | -------------------------------------------------------------------- | -------- | ------ | -------------- |
| Non-blocking MQTT publish in Bridge | Address TODO in `mqtt.cpp` (queue vs busy-wait).                     | Medium   | Large  | Pi testing     |
| Softer wireless module recovery     | Task restart vs `machine.reset()` per FIXME in `wireless_module.py`. | Medium   | Medium | MicroPython HW |
| Normal compile for DPS368           | No `#include "DPS368.cpp"` from `main.cpp`.                          | Low      | Small  | Build system   |


## Testing and QA


| Title                        | Description                                                                | Priority | Effort | Dependencies        |
| ---------------------------- | -------------------------------------------------------------------------- | -------- | ------ | ------------------- |
| DAS unit / integration tests | Add pytest coverage; `pytest` is listed but tests are absent under `DAS/`. | High     | Large  | Mock or test broker |
| HIL checklist                | ESP32 + Pi integration procedure.                                          | Medium   | Medium | Lab hardware        |
| Bridge integration test      | Dedup + banned-topic behavior across two brokers or loopback.              | Medium   | Large  | Radios              |


## DevOps / deployment


| Title                           | Description                                                                               | Priority | Effort | Dependencies  |
| ------------------------------- | ----------------------------------------------------------------------------------------- | -------- | ------ | ------------- |
| Validate `logger.service` paths | `ExecStart` references `V3_mqtt_recorder.py` — confirm cwd and Poetry env on deployed Pi. | High     | Small  | Deploy layout |
| Document SSH / `mhp` install    | Extend `services/README.md` as needed for keys and Poetry.                                | Medium   | Small  | Org GitHub    |
| CI toolchain pins               | Optional: Node/Python version matrix for ANT+ and DAS.                                    | Low      | Medium | CI platform   |


