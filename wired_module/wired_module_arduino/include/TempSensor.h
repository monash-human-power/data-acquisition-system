#ifndef TEMP_SENSOR_H
#define TEMP_SENSOR_H

#include "I2cSensorBase.h"

/*
SHT4x temp/humidity sensor

configure(): reset/presence check, no continuous measurement like baro
read(): send command to trigger high precison reading
generateJson():
send():

*/

class TempSensor : public I2cSensorBase {

public:

    // Constructor
    TempSensor(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID);

    void configure() override;
    void read() override;
    String generateJson() override;
    // void send() override;

private:

    // Measurements
    float temperature = 0.0f;
    float humidity = 0.0f;
    // bool valid = false // crc check? is this necessary idk

    // Commands
};



#endif