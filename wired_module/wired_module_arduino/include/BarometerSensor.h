#include "I2cSensorBase.h"

#ifndef BAROMETER_SENSOR
#define BAROMETER_SENSOR

class BarometerSensor : public I2cSensorBase {
   public:
    // Attributes
    const int scaleFactor = 524288;
    int16_t c0;
    int16_t c1;

    // Use parent constructor
    using I2cSensorBase::I2cSensorBase;

    // Methods
    void configure() override;
    void read() override;
};

#endif