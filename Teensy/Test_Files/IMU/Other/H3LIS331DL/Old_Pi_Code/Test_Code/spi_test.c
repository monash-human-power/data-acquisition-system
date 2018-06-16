

// =========================== PROGRAM SETUP =================================

#include <stdio.h>
#include <pigpio.h>

// ACCELEROMETER REGISTERS
#define CTRL_REG1   0x20
#define CTRL_REG4   0x23
#define DATAX0      0x28

// ACCELEROMETER SETTINGS
#define CTRL_REG1_CONTENTS 0b00111111   // Normal Mode, 1000Hz ODR, Enable axes
#define CTRL_REG4_CONTENTS 0b00000000   // +-100g (change bits 2/3 - 00 = 100g, 01 = 200g, 11 = 400g)

// SPI COMMUNICATION BYTES
#define MULTI_BIT       0x40
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
    int H3LIS331DL, bytes;

    // Intialize gpio pins
    if (gpioInitialise() < 0)
    {
        printf("Failed to initialize GPIO!");
        return 1;
    }

    // -------------------------- SET UP SPI DEVICE --------------------------

    // Define new spi device
    H3LIS331DL = spiOpen(0, speedSPI, 3);

    data[0] = CTRL_REG1 | MULTI_BIT;
    data[1] = CTRL_REG1_CONTENTS;
    spiWrite(H3LIS331DL, data, 2);
    printf("\nH3LIS331DL=%x,data[0]=%x,data[1]=%x\n\n",H3LIS331DL,data[0],data[1]);

    data[0] = CTRL_REG4 | MULTI_BIT;
    data[1] = CTRL_REG4_CONTENTS;
    spiWrite(H3LIS331DL, data, 2);
    printf("\nH3LIS331DL=%x,data[0]=%x,data[1]=%x\n\n",H3LIS331DL,data[0],data[1]);

    // --------------------------- INITIALIZE READ ---------------------------

    // Need a warm up segment to initialize readings
    for (i = 0; i < coldStartSamples; i++) {
        data[0] = DATAX0 | MULTI_BIT | READ_BIT;
        bytes = spiXfer(H3LIS331DL, data, data, 7);
        printf("bytes = %d,data was %x %x %x %x %x %x %x %x\n\n",bytes,data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]);
        time_sleep(coldStartDelay);
    }

    // --------------------------- READ DATA ---------------------------

    data[0] = DATAX0 | MULTI_BIT | READ_BIT;
    bytes = spiXfer(H3LIS331DL, data, data, 7);
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
