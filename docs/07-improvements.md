# 7. Improvement recommendations

## Architecture

- **Unify or document MQTT namespaces**: Wired firmware uses `sensor/{hex}`; wireless uses `/v3/wireless_module/...`. A small **gateway** on the Pi or explicit consumer documentation reduces dashboard and recorder complexity.
- **Crash alerts**: Parameterize wireless module ID (currently fixed to module `3` in `crash_alert/main_crash_alert.py`) and optional SNS / multi-channel senders (`SnsMessageSender` exists but is not registered in `CrashAlert`).
- **Bridge**: Move broker URL and banned-topic rules to **config** (file or env) — aligns with the TODO in `Bridge/src/bridge.cpp`.

## Performance

- **Bridge**: Replace blocking `publish` (wait until connected) with a **send queue** and backpressure policy — see TODO in `Bridge/src/mqtt.cpp`.
- **Radio bandwidth**: The bridge already drops high-rate topic names (`mpu_data`, `crash_detection`, `strain_gauge`); keep any new high-rate streams off the radio path or rate-limit explicitly.

## Scalability

- **Logging**: SQLite single-file sessions are fine for development; for long campaigns, define **rotation**, archival, and optionally a time-series store (not present today).

## Code quality and safety

- **Firmware**: Fix invalid nested `loop()` in `wired_module/vm code 2.1/src/main.cpp` and the infinite `setup()` loop in `wired_module/wired_module_arduino/src/main.cpp` — these are correctness bugs.
- **Tests**: Add **pytest** coverage under `DAS/`; dependencies are declared but tests are missing.
- **MicroPython**: Prefer restarting tasks over full `**machine.reset()`** where safe (`wireless_modules/wireless_module.py` FIXME).
- **Build hygiene**: Avoid `#include "DPS368.cpp"` from `main.cpp`; compile DPS368 as its own translation unit.

