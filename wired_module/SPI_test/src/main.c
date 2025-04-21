#include "driver/spi_master.h"

/*
MPU9250 spi operational features:
    data is MSD first
    data is send on the rising edge of clk
    data is transitioned on the falling edge of clk
    max freq of clk is 1MHz

    SPI address format:
    MSB                                            LSB
    R/W     A6      A5      A3      A2      A1      A0

    
    
    SPI mode, representing a pair of (CPOL, CPHA) configuration:
        - 0: (0, 0)
        - 1: (0, 1)
        - 2: (1, 0)
        - 3: (1, 1)

    CPOL = 1 , clock line idle high in the datasheet
    CPHA = 1 , based on the operational feature of data send on rising edge and transition on falling edge

    therefore spi mode is 3


 */

void app_main() {
    
    spi_bus_config_t buscfg = {
        .miso_io_num = 19,
        .mosi_io_num = 23,
        .sclk_io_num = 18,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 32,
    };

    spi_bus_initialize(VSPI_HOST,&buscfg,1);

    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 1000000, // Clock out at 1 MHz with 1 us cycle
        .mode = 3,                 // SPI mode 0 - the clock signal starts with a low signal
        .spics_io_num = 5,        // CS pin GPIO5 
        .queue_size = 7,           // Queue 7 transactions at a time
    };

    spi_transaction_t trans;
    // Define SPI handle
    spi_device_handle_t mpu_handle;
    spi_bus_add_device(VSPI_HOST, &devcfg, &mpu_handle);

    spi_device_transmit

}