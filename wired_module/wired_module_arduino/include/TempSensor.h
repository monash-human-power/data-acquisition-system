#ifndef TEMP_SENSOR_H
#define TEMP_SENSOR_H

#include "I2cSensorBase.h"
#include "driver/i2c.h"
#include <Arduino.h>

/*
SHT4x temp/humidity sensor

configure(): reset/presence check from serial number, no continuous measurement like baro
read(): send command to trigger high precison reading
generateJson(): {"sensor":"sht4x", "temperature":...,"humidity"}
send(): ??

*/

class TempSensor : public I2cSensorBase {

public:

    // Constructor
    TempSensor(i2c_port_t masterPortNum, uint8_t sensorAddress, uint8_t sensorID)
        : I2cSensorBase(masterPortNum, sensorAddress, sensorID) {};

    void configure() override;
    void read() override;
    String generateJson() override;
    // void send() override;

private:

    // Measurements
    float temperature = 0.0f;
    float humidity = 0.0f;
    bool valid = false // crc check? is this necessary idk

    // Helper funcs
    static float convert_temp(uint16_t raw_temp);
    static float convert_humidity(uint16_t raw_humidity);
    static uint8_t crc8(const uint8_t* data, size_t len);
    static bool check_word_crc(const uint8_t *w);
    
    /* [TO DO]
     - serial_read check
    */
 
};

#endif