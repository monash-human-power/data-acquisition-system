#include "I2cSensorBase.h"

#ifndef DPS368_H
#define DPS368_H

// header guard
#define DPS368_ADDRESS (0x76 << 1) 
#define DPS368_ID 0x10


// register map for the DPS368
#define DPS368_PSR_B2      0x00
#define DPS368_PSR_B1      0x01
#define DPS368_PSR_B0      0x02
#define DPS368_TMP_B2      0x03
#define DPS368_TMP_B1      0x04
#define DPS368_TMP_B0      0x05
#define DPS368_PRS_CFG     0x06
#define DPS368_TMP_CFG     0x07
#define DPS368_MEAS_CFG    0x08
#define DPS368_CFG_REG     0x09
#define DPS368_INT_STS     0x0A
#define DPS368_FIFO_STS    0x0B
#define DPS368_RESET       0x0C
#define DPS368_PRODUCT_ID  0x0D
#define DPS368_COEF        0x10  // Starts at 0x10, spans multiple addresses
#define DPS368_RESERVED    0x22  // Starts at 0x22, spans multiple addresses
#define DPS368_COEF_SRCE   0x28


/**
 * From the section 8.5 of the datasheet (Sensor Operating Mode and Status) 
 * Set measurement mode and type:
    Standby Mode
    000 - Idle / Stop background measurement
    Command Mode
    001 - Pressure measurement
    010 - Temperature measurement
    011 - na.
    100 - na.
    Background Mode
    101 - Continous pressure measurement
    110 - Continous temperature measurement
    111 - Continous pressure and temperature measurement
 */
enum DPS368Mode {
    IDLE = 0x00,
    CMD_PRS = 0x01,
    CMD_TMP = 0x02,
    CON_TMP = 0x06,
    CON_PRS = 0x05,
    CON_BOTH = 0x07
};

class DPS368:public I2cSensorBase {

    public:
    // Attributes


    // Use parent constructor
    using I2cSensorBase::I2cSensorBase;

    // Methods
    void configure() override;
    void read() override;

    boolean is_coef_ready();
    boolean is_sensor_ready();

    void get_coefficient();
    
    void select_mode(DPS368Mode measurementMode);

};

#endif // DPS368_H