

// =========================== PROGRAM SETUP =================================

#include <stdio.h>
#include <pigpio.h>

// ACCELEROMETER REGISTERS
#define CTRL1_XL        0x10    // ODR, Scale
#define CTRL6_C         0x15    // Power Mode
#define CTRL9_XL        0x18    // Enable axies
#define INT1_CTRL       0x0D
#define WHO_AM_I        0x0F
#define DATAX0          0x28    // Start address for reading accelerometer registers

// ACCELEROMETER SETTINGS
#define CTRL1_XL_CONTENTS   0b10100100    // +/-16 g, 6667 Hz
#define CTRL6_C_CONTENTS    0b00000000
#define CTRL9_XL_CONTENTS   0b00111000
#define INT1_CTRL_CONTENTS  0b00000001

// SPI COMMUNICATION BYTES
#define MULTI_BIT       0x00//0x04    // SPI multi-bit communication
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
    int LSM6DS3, bytes;

    // Intialize gpio pins
    if (gpioInitialise() < 0)
    {
        printf("Failed to initialize GPIO!");
        return 1;
    }

    // -------------------------- SET UP SPI DEVICE --------------------------

    // Define new spi device
    LSM6DS3 = spiOpen(0, speedSPI, 3);

    data[0] = CTRL9_XL | MULTI_BIT;
    data[1] = CTRL9_XL_CONTENTS;
    spiWrite(LSM6DS3, data, 2);
    printf("\nLSM6DS3=%x,data[0]=%x,data[1]=%x\n\n",LSM6DS3,data[0],data[1]);

    data[0] = CTRL6_C | MULTI_BIT;
    data[1] = CTRL6_C_CONTENTS;
    spiWrite(LSM6DS3, data, 2);
    printf("LSM6DS3=%x,data[0]=%x,data[1]=%x\n\n",LSM6DS3,data[0],data[1]);

    data[0] = CTRL1_XL | MULTI_BIT;
    data[1] = CTRL1_XL_CONTENTS;
    spiWrite(LSM6DS3, data, 2);
    printf("LSM6DS3=%x,data[0]=%x,data[1]=%x\n\n",LSM6DS3,data[0],data[1]);

    data[0] = INT1_CTRL | MULTI_BIT;
    data[1] = INT1_CTRL_CONTENTS;
    spiWrite(LSM6DS3, data, 2);
    printf("LSM6DS3=%x,data[0]=%x,data[1]=%x\n\n",LSM6DS3,data[0],data[1]);

    // --------------------------- INITIALIZE READ ---------------------------

    // Need a warm up segment to initialize readings
    for (i = 0; i < coldStartSamples; i++) {
        data[0] = DATAX0 | MULTI_BIT | READ_BIT;
        bytes = spiXfer(LSM6DS3, data, data, 7);
        printf("bytes = %d,data was %x %x %x %x %x %x %x %x\n\n",bytes,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]);
        time_sleep(coldStartDelay);
    }

    // --------------------------- READ DATA ---------------------------

    data[0] = DATAX0 | MULTI_BIT | READ_BIT;
    bytes = spiXfer(LSM6DS3, data, data, 7);
    printf("bytes = %d,data was %x %x %x %x %x %x %x %x\n\n",bytes,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]);

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
