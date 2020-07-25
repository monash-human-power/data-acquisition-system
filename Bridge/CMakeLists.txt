cmake_minimum_required(VERSION 3.6)
project(ZetaBridge)

# Build ZetaRF
add_subdirectory(ZetaRF)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/build)

add_compile_definitions(WIRINGPI)
include_directories(ZetaRF/src)

#file(GLOB_RECURSE CONFIG_SOURCES "src/configs/*.cpp")
set(SOURCES
    "src/main.cpp"
    "src/protocol.cpp"
)

add_executable(${PROJECT_NAME} src/main.cpp ${SOURCES})
target_link_libraries(${PROJECT_NAME} zetarf)