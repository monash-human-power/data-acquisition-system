#include "I2cSensorBase.h"

#ifndef MPU_SENSOR
#define MPU_SENSOR

class MpuSensor : public I2cSensorBase {
   public:
    // Use parent constructor
    using I2cSensorBase::I2cSensorBase;

    // Methods
    void configure() override;
    void read() override;
};

#endif