#include "Camera.h"

#include <format>
#include <cstdlib>

Camera::Camera(uint8_t deviceIndex)  : cameraIndex(deviceIndex) {
}

Camera::~Camera() {
}

bool Camera::record(uint16_t timeSeconds, std::string savePath) {
    std::string cmd = std::format("rpicam-vid --camera -t {}s -o {} &", cameraIndex, timeSeconds, savePath);
    int result = system(cmd.c_str());

    if (result == 0) {
        return true;
    }
    else {
        return false;
    }
}
