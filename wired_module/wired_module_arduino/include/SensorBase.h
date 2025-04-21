#include <CAN.h>

#ifndef SENSOR_BASE
#define SENSOR_BASE

// Abstract Class
class SensorBase {
   public:
    // Attributes
    uint8_t canBuffer[4];
    uint8_t sensorID;

    // Abstract methods
    virtual void configure() = 0;
    virtual void read() = 0;

    // Methods
    void send() {
        CAN.beginPacket(this->sensorID);
        this->read();                                         // Read data from sensor and store in buffer
        CAN.write(this->canBuffer, sizeof(this->canBuffer));  // Send packet
        CAN.endPacket();
    }
};

#endif