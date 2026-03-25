# 2. Codebase breakdown

## High-level architecture

- **Embedded + edge**: ESP32 (Arduino-style C++), ESP32 **MicroPython** wireless modules, **Raspberry Pi** for DAS scripts, radio bridge, ANT+ logger, systemd services.
- **Messaging hub**: **MQTT** (local broker); optional **radio bridge** between two MQTT deployments (`Bridge/README.md`).
- **Not** a single monolithic server: **scripts and firmware** integrated via MQTT topic conventions and the shared **`mhp`** Python package (`DAS/pyproject.toml` git dependency).

## Folder structure

| Path | Role |
|------|------|
| `DAS/` | Poetry Python package: MQTT recorder/playback, fake module, log→Excel |
| `Bridge/` | C++ CMake: Paho MQTT C++ + ZetaRF submodule, MQTT ↔ radio |
| `wireless_modules/` | MicroPython on ESP32: sensors + `WirelessModule` + `mqtt_client.py` |
| `wireless_modules_py/` | Async Python wireless module using `mhp` topics |
| `wired_module/` | ESP32 C++ — `wired_module_arduino`, `vm code 2.1`, SPI/I2C tests (`AdcTest2`, `SPI_test`) |
| `ant_plus_sensor/` | Node.js: ANT+ → MQTT (`ant_plus_logger.js`) |
| `crash_alert/` | Python: MQTT subscriber → Slack (`SlackMessageSender`; `SnsMessageSender` exists but is not wired in `CrashAlert`) |
| `utils/` | `turps.py` — Excel interpolation to unified CSV |
| `services/` | systemd unit examples (`logger.service`, `ant-plus.service`, …) |

## Key modules and responsibilities

- **`WirelessModule`** (`wireless_modules/wireless_module.py`): aggregates sensor readings, MQTT publish, subscribes to `v3/start`, battery loop, crash/mpu topics; error handler may **`machine.reset()`** after delay.
- **`SensorBase`** (`wired_module/vm code 2.1/include/SensorBase.h`): `configure` / `read` / `generateJson`; `send()` publishes to `sensor/%02x` via global `mqttClient`.
- **`Bridge`** (`Bridge/src/bridge.cpp`): deduplicates bridged traffic via hashed topic+payload; **drops** topics whose names contain `mpu_data`, `crash_detection`, or `strain_gauge` (hardcoded).
- **`MqttBridgeClient::publish`** (`Bridge/src/mqtt.cpp`): waits until MQTT is connected before publish (TODO: queue).
- **`CrashAlertDriver`** (`crash_alert/main_crash_alert.py`): subscribes to `topics.WirelessModule.id(3).crash_alert` — **module ID 3 is fixed in code**.

## Data flow (summary)

1. **Wireless**: sensors → `WirelessModule._read_sensors` → JSON on `/v3/wireless_module/{id}/data`.
2. **Wired ESP32**: `SensorBase::sendJson` → `sensor/{hex id}` (distinct from `/v3/wireless_module/...`).
3. **Pi / logging**: `V3_mqtt_recorder` subscribes to chosen topics and writes SQLite.
4. **Optional**: `ZetaBridge` mirrors MQTT between brokers over RF, with filters and loop prevention.

## Design patterns (observed)

- **Template method**: `SensorBase` with `configure` / `read` / `generateJson`.
- **Strategy**: `message_senders` base + `SlackMessageSender` (extensible).
- **Observer / callbacks**: MQTT and radio callbacks in `Bridge`.
- **Deduplication**: `recently_sent_messages_` in `Bridge` to avoid bridge echo loops.

## External dependencies

- **Python** (`DAS/pyproject.toml`): `paho-mqtt`, `pandas`, `rich`, `mqtt-logger`, `mhp` from `monash-human-power/common` (SSH), etc.
- **C++ Bridge**: Paho MQTT C++, ZetaRF (submodule), RF24 (see `Bridge/README.md`), **wiringpi**.
- **Embedded**: Arduino `WiFi`, `PubSubClient`, `ArduinoJson` (`SensorBase.h`); MicroPython `umqtt.simple`.
- **Node** (`ant_plus_sensor/package.json`): `mqtt`, `ant-plus`, `winston`.
