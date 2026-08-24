#pragma once

#include <string>

class Camera
{
protected:
    uint8_t cameraIndex;

public:
    explicit Camera(uint8_t deviceIndex);

    ~Camera();

    bool record(uint16_t timeSeconds,
                std::string savePath);

};