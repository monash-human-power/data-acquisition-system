#ifndef GYRO_SENSOR_H
#define GYRO_SENSOR_H

#include "I2cSensorBase.h"

class ICM42670: public I2cSensorBase {
public:
    // Gyroscope values
    float gyroX, gyroY, gyroZ;

    // Constructor
    ICM42670(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID);

    // Override required methods
    void configure() override;
    void read() override;
    String generateJson() override;
};

#endif // GYRO_SENSOR_H

