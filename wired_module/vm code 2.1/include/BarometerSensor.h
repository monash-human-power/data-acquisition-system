#ifndef BAROMETER_SENSOR_H
#define BAROMETER_SENSOR_H

#include "I2cSensorBase.h"

class BarometerSensor : public I2cSensorBase {
public:
    using I2cSensorBase::I2cSensorBase; // inherit constructors

    void configure() override;
    void read() override;
    String generateJson() override;
    void send() override;

private:
    int16_t c0 = 0;
    int16_t c1 = 0;
    float temperature = 0.0f;
    static constexpr int scaleFactor = 524288; // or 1048576, pick one
};

#endif
