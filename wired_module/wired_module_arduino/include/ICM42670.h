#ifndef GYRO_SENSOR_H
#define GYRO_SENSOR_H

#include "SpiSensorBase.h"

class GyroSensor: public SpiSensorBase {
public:
    // Gyroscope values
    float gyroX, gyroY, gyroZ;

    // Constructor
    GyroSensor(spi_device_handle_t handle, uint8_t sensorID);

    // Override required methods
    void configure() override;
    void read() override;
    String generateJson() override;
};

#endif // GYRO_SENSOR_H

