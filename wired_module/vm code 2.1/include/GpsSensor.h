#ifndef GPSSENSOR_H
#define GPSSENSOR_H

#include "SensorBase.h"
#include <HardwareSerial.h>
#include <string>

class GpsSensor : public SensorBase {
public:
    // Constructor
    GpsSensor(int uartNum, int rxPin, int txPin, uint8_t canId);

    // Methods
    void configure() override;
    void read() override;
    String generateJson() override;
    void send() override;

private:
    // GPS related attributes
    HardwareSerial* gpsSerial;
    int uartNum;
    int rxPin;
    int txPin;
    String buffer;
};

#endif // GPSSENSOR_H
