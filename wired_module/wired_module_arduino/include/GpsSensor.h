#ifndef GPSSENSOR_H
#define GPSSENSOR_H

#include "SensorBase.h"
#include <HardwareSerial.h>
#include <string>

class GpsSensor : public SensorBase {
public:
    GpsSensor(int uartNum, int rxPin, int txPin, uint8_t canId);
    void configure() override;
    void read() override;

private:
    HardwareSerial* gpsSerial;
    int uartNum;
    int rxPin;
    int txPin;
    String buffer;
};

#endif
