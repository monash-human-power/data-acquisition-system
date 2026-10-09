#pragma once

#include <cstdint>

class Camera
{
private:
    uint8_t cameraIndex;

public:
    explicit Camera(uint8_t deviceIndex = 0);

    bool startStream();
    void stopStream();
};