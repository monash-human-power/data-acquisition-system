#include "driver/i2c.h"

#ifndef I2C_MASTER
#define I2C_MASTER

class I2cMaster {
   public:
    // Attributes
    i2c_port_t portNum;

    // Constructor
    I2cMaster(i2c_port_t portNum, int sda, int scl, int clockFrequency);

    // Destructor
    ~I2cMaster();
};

#endif