

// =========================== PROGRAM SETUP =================================

#include <stdio.h>
#include <pigpio.h>

// ACCELEROMETER REGISTERS
#define DATA_FORMAT     0x31    // Data_Format register address (influences 3 or 4 wire SPI, +-2g, +-4g, +-8g, +-16g)
#define BW_RATE         0x2C    // BW_Rate register address (influences ODR)
#define POWER_CTL       0x2D    // Power_CTL register address (influences Auto-sleep, Standby, Sleep, Wakup functions)
#define DATAX0          0x32    // Start address for reading accelerometer registers

// ACCELEROMETER SETTINGS
#define FORMAT_CONTENTS 0x0B    // bits to write to data format register = +/- 16g range, 13-bit resolution (p. 26 of ADXL345 datasheet)
#define BW_CONTENTS     0x0F    // Normal operation, 3200Hz
#define POWER_CONTENTS  0x08    // Measurement mode, 2Hz readings in sleep mode

// SPI COMMUNICATION BYTES
#define MULTI_BIT       0x40    // SPI multi-bit communication
#define READ_BIT        0x80
const int coldStartSamples = 2;  // number of samples to be read before outputting data to console (cold start delays)
const double coldStartDelay = 0.1;  // time delay between cold start reads
const int speedSPI = 5000000;  // SPI communication speed, bps

// =========================== FUNCTION MAIN =================================
int main(int argc, char const *argv[])
{
    // SPI Variables
    int i;
    char data[7];
    int ADXL345, bytes;

    // Intialize gpio pins
    if (gpioInitialise() < 0)
    {
        printf("Failed to initialize GPIO!");
        return 1;
    }

    // -------------------------- SET UP SPI DEVICE --------------------------

    // Define new spi device
    ADXL345 = spiOpen(0, speedSPI, 3);
    printf("ADXL345=%d",ADXL345);

    // Write to BW_RATE Register
    data[0] = BW_RATE | MULTI_BIT;
    data[1] = BW_CONTENTS;
    spiWrite(ADXL345, data, 2);
    printf("ADXL345=%d,data[0]=%d,data[1]=%d\n\n",ADXL345,data[0],data[1]);

    // Write to DATA_FORMAT Register
    data[0] = DATA_FORMAT | MULTI_BIT;
    data[1] = FORMAT_CONTENTS;
    spiWrite(ADXL345, data, 2);
    printf("ADXL345=%d,data[0]=%d,data[1]=%d\n\n",ADXL345,data[0],data[1]);

    // Write to POWER_MODE Register
    data[0] = POWER_CTL | MULTI_BIT;
    data[1] = POWER_CONTENTS;
    spiWrite(ADXL345, data, 2);
    printf("ADXL345=%d,data[0]=%d,data[1]=%d\n\n",ADXL345,data[0],data[1]);

    // --------------------------- INITIALIZE READ ---------------------------

    // Need a warm up segment to initialize readings
    for (i = 0; i < coldStartSamples; i++) {
        data[0] = DATAX0 | MULTI_BIT | READ_BIT;
        bytes = spiXfer(ADXL345, data, data, 7);
        printf("bytes = %d,data was %x %x %x %x %x %x %x %x\n\n",bytes,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]);
        time_sleep(coldStartDelay);
    }

    // --------------------------- READ DATA ---------------------------

    data[0] = DATAX0 | MULTI_BIT | READ_BIT;
    bytes = spiXfer(ADXL345, data, data, 7);
    printf("bytes=%d,data was %x %x %x %x %x %x %x %x\n\n",bytes,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]);

    // Process bytes on last read
    if (bytes == 7)
    {
        printf("Success!\n\n");
    }
    else
    {
        printf("Error!\n\n");
    }

    gpioTerminate();

    return 0;
}
