#include "BarometerSensor.h"
#include "SensorBase.h"

#include <cstring>

class BarometerSensor : public SensorBase {
public:
    BarometerSensor() : c0(0), c1(0), temperature(0.0f) {}

    void configure() override {
        // use external sensor
        write_sensor_register(0x07, 0x80, 1000);

        // set to continuous temperature measurement 
        write_sensor_register(0x08, 0x06, 1000);

        // get coefficients
        read_sensor_register(0x10, 3, 1000);

        this->c0 = this->readBuffer[0] << 4 | this->readBuffer[1] >> 4;
        if (this->c0 & (1 << 11))
            this->c0 |= 0xF000;

        this->c1 = ((this->readBuffer[1] & 0xF) << 8) | this->readBuffer[2];
        if (this->c1 & (1 << 11))
            this->c1 |= 0xF000;
    }

    void read() override {
        // Get raw data from sensor
        read_sensor_register(0x03, 3, 1000);

        int32_t raw_temp = (this->readBuffer[0] << 8) | this->readBuffer[1];
        raw_temp = (raw_temp << 8) | this->readBuffer[2];

        if (raw_temp & (1 << 23)) {
            raw_temp |= 0xFF000000;
        }

        float temp = static_cast<float>(raw_temp) / static_cast<float>(this->scaleFactor);
        this->temperature = this->c0 * 0.5f + this->c1 * temp;
    }

    String generateJson() override {
        return "{\"sensors\":[{\"type\":\"barometer\",\"value\":" + String(this->temperature, 2) + "}]}";
    }

    void send() override {
        sendJson(0x124, generateJson());
    }

private:
    int16_t c0, c1;
    float temperature;
    static constexpr int scaleFactor = 1048576;
};
