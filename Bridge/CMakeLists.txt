cmake_minimum_required(VERSION 3.6)
project(ZetaBridge)


set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)

# Build/configure ZetaRF
#add_compile_definitions(WIRINGPI)
#include_directories(libs/ZetaRF/src)
#add_subdirectory(libs/ZetaRF)

# Build/configure paho.mqtt.cpp
include_directories(libs/paho.mqtt.cpp/src)
add_subdirectory (libs/paho.mqtt.cpp)

#file(GLOB_RECURSE CONFIG_SOURCES "src/configs/*.cpp")
set(SOURCES
    "src/main.cpp"
    "src/protocol.cpp"
)

add_executable(${PROJECT_NAME} ${SOURCES})
#target_link_libraries(${PROJECT_NAME} zetarf)
target_link_libraries(${PROJECT_NAME} paho-mqttpp3)