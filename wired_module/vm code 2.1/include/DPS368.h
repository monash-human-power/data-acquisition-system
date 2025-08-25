#ifndef DPS368_H
#define DPS368_H

#include "I2cSensorBase.h"

// I2C address and ID
#define DPS368_ADDRESS 0x76
#define DPS368_ID      0x10   // 8-bit product ID

// Sensor config
#define TMP_MEASUREMENT_RATE 8
#define TMP_OVERSAMPLING_RATE 16
#define PSR_MEASUREMENT_RATE 8
#define PSR_OVERSAMPLING_RATE 16

#define TMP_CONFIG ((uint8_t)((log2(TMP_MEASUREMENT_RATE) << 4) + log2(TMP_OVERSAMPLING_RATE)))
#define PSR_CONFIG ((uint8_t)((log2(PSR_MEASUREMENT_RATE) << 4) + log2(PSR_OVERSAMPLING_RATE)))

// Register map
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
#define DPS368_COEF        0x10
#define DPS368_COEF_SRCE   0x28

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
    using I2cSensorBase::I2cSensorBase;

    void configure() override;
    void read() override;
    String generateJson() override;
    void send() override;

private:
    int16_t c0 = 0, c1 = 0;
    int32_t c00 = 0, c10 = 0;
    int16_t c01 = 0, c11 = 0, c20 = 0, c21 = 0, c30 = 0;

    float temperature = 0.0f;
    float pressure = 0.0f;

    uint8_t coef_source = 0;

    bool is_coef_ready();
    bool is_sensor_ready();
    void get_coef_source();
    void read_coefficients();
    void select_mode(DPS368Mode mode);
    int32_t read_raw_temperature();
    int32_t read_raw_pressure();
    void calculate_temperature();
    void calculate_pressure();
    uint32_t get_scale_factor(uint8_t oversamplingRate);
};

#endif // DPS368_H
