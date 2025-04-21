#include "I2cMaster.h"

I2cMaster::I2cMaster(i2c_port_t portNum, int sda, int scl, int clockFrequency) {
    this->portNum = portNum;
    i2c_config_t masterConfig = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = sda,
        .scl_io_num = scl,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master = {
            .clk_speed = clockFrequency,
        }};

    i2c_param_config(portNum, &masterConfig);
    ESP_ERROR_CHECK(i2c_driver_install(portNum, masterConfig.mode, 0, 0, 0));
}

I2cMaster::~I2cMaster() {
    ESP_ERROR_CHECK(i2c_driver_delete(this->portNum));
}