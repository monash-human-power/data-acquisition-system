#include "I2cSensorBase.h"

#ifndef GYRO_SENSOR
#define GYRO_SENSOR

class GyroSensor : public I2cSensorBase {
public:
    // Use parent constructor
    using I2cSensorBase::I2cSensorBase;

    // Methods
    void configure() override;
    void read() override;
    String generateJson() override;
    void send() override;

private:
    float gyroX, gyroY, gyroZ;
};

#endif
