#ifndef DPS368_H
#define DPS368_H

#include "I2cSensorBase.h"

// header guard
#define DPS368_ADDRESS (0x76 << 1) 
#define DPS368_ID 0x10

// sensor configuration
#define TMP_MEASUREMENT_RATE 8
#define TMP_OVERSAMPLING_RATE 16
#define PSR_MEASUREMENT_RATE 8
#define PSR_OVERSAMPLING_RATE 16

// To be written into the configuration register
#define TMP_CONFIG (uint8_t)(log2(TMP_MEASUREMENT_RATE) << 4 + (uint8_t)log2(TMP_OVERSAMPLING_RATE))
#define PSR_CONFIG (uint8_t)(log2(PSR_MEASUREMENT_RATE) << 4 + (uint8_t)log2(PSR_OVERSAMPLING_RATE))

// register map for the DPS368
#define DPS368_PSR         0x00
#define DPS368_TMP         0x03
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

// Measurement modes as per datasheet
enum DPS368Mode {
    IDLE = 0x00,
    CMD_PRS = 0x01,
    CMD_TMP = 0x02,
    CON_TMP = 0x06,
    CON_PRS = 0x05,
    CON_BOTH = 0x07
};

class DPS368 : public I2cSensorBase {
public:
    // Attributes
    uint8_t coef_source;

    // Use parent constructor
    using I2cSensorBase::I2cSensorBase;

    // Methods
    void configure() override;
    void read() override;
    String generateJson() override;
    void send() override;

    boolean is_coef_ready();
    boolean is_sensor_ready();
    
    uint8_t get_coef_source();
    uint32_t get_scale_factor(uint8_t oversamplingRate);
    void get_coefficient();
    
    void select_mode(DPS368Mode measurementMode);
    int32_t read_raw_temperature();
    void calculate_temperature();
    int32_t read_raw_pressure();
    void calculate_pressure();

private:
    // Coefficients for calculation
    int16_t c0, c1; // 12bits
    int32_t c00, c10; // 20bits
    int16_t c01, c11, c20, c21, c30; // 16bits
};

#endif // DPS368_H
