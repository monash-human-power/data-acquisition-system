#ifndef MPU_SENSOR_H
#define MPU_SENSOR_H

#include "I2cSensorBase.h"

class MpuSensor : public I2cSensorBase {
public:
    // Use the parent constructor
    using I2cSensorBase::I2cSensorBase;

    // Methods
    void configure() override;
    void read() override;
    String generateJson() override;  // Declare generateJson function
    void send() override;            // Declare send function
};

#endif // MPU_SENSOR_H
