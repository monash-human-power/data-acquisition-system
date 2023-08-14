cmake_minimum_required(VERSION 3.6)
project(ZetaBridge)


set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)

# Build/configure ZetaRF
add_compile_definitions(WIRINGPI)
include_directories(libs/ZetaRF/src)
add_subdirectory(libs/ZetaRF)

# Build/configure paho.mqtt.cpp
include_directories(libs/paho.mqtt.cpp/src)
add_subdirectory (libs/paho.mqtt.cpp)

set(SOURCES
    "src/bridge.cpp"
    "src/debug.cpp"
    "src/frame.cpp"
    "src/main.cpp"
    "src/mqtt.cpp"
    "src/nrf24.cpp"
    "src/protocol.cpp"
    "src/radio.cpp"
    "src/zeta.cpp"
    "src/rf_config/si4455_revb1_bidir_fixed_crc_pre10_sync3MHP_pay8_433mhz_40kbps.cpp"
)

add_executable(${PROJECT_NAME} ${SOURCES})
target_link_libraries(${PROJECT_NAME} zetarf)
target_link_libraries(${PROJECT_NAME} paho-mqttpp3)
target_link_libraries(${PROJECT_NAME} rf24 pigpio)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
# Add compile definition MQTT_BRIDGE_DEBUG if we're building debug
target_compile_definitions(${PROJECT_NAME} PUBLIC "$<$<CONFIG:DEBUG>:MQTT_BRIDGE_DEBUG>")