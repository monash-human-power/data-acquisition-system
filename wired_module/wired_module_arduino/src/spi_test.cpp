#include <Arduino.h>
#include "driver/spi_master.h"

#define PIN_MOSI 11
#define PIN_MISO 13
#define PIN_SCLK 12
#define PIN_CS   10

static spi_device_handle_t mpu;

void setup() {
  Serial.begin(115200);
  delay(50);

// bus configuration
  spi_bus_config_t buscfg = {};
  buscfg.mosi_io_num = PIN_MOSI;
  buscfg.miso_io_num = PIN_MISO;
  buscfg.sclk_io_num = PIN_SCLK;
  buscfg.quadwp_io_num = -1;
  buscfg.quadhd_io_num = -1;
  buscfg.max_transfer_sz = 64;
  ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));

// senseor device config
  spi_device_interface_config_t devcfg = {};
  devcfg.clock_speed_hz = 1 * 1000 * 1000; // 1 MHz bring-up
  devcfg.mode = 0;                         // CPOL=0, CPHA=0
  devcfg.spics_io_num = PIN_CS;            // hardware CS
  devcfg.queue_size = 1;
  ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &mpu));

// read WHO AM I
  uint8_t tx[2] = { uint8_t(0x75 | 0x80), 0x00 };
  uint8_t rx[2] = { 0, 0 };

  spi_transaction_t t = {};
  t.length = 16;        // bits total (addr + data)
  t.tx_buffer = tx;
  t.rx_buffer = rx;

  esp_err_t err = spi_device_transmit(mpu, &t);
  uint8_t who = rx[1];

  if (err != ESP_OK) {
    Serial.printf("transmission error: %d\n", (int)err);
    return;
  }

  Serial.printf("WHO_AM_I = 0x%02X", who);

  if (who == 0x68 || who == 0x70 || who == 0x71) {
    Serial.println("SPI ok");
  } else {
    Serial.println("unexpected value");
  }
}

void loop() {
  delay(1000);
}
