#pragma once

#include "SPIBus.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

// Driver for the TI ADS131M08 8-channel, 24-bit simultaneous-sampling ADC.
//
// SPI notes (see ADS131M08 datasheet, section 8.5):
//   - SPI mode 1 (CPOL = 0, CPHA = 1), SCLK up to 25 MHz.
//   - Default word length is 24 bits. Every frame is 10 words (30 bytes):
//       input:  command, [register data...], [CRC], padding
//       output: response, CH0 ... CH7, CRC
//   - The response to a command arrives in the *next* frame.
//   - CS must stay low for the whole frame, which a single
//     SPIBus::transfer() call guarantees.
//
// The driver keeps the default 24-bit word length.
class ADS131M08
{
public:
    static constexpr int NUM_CHANNELS = 8;
    static constexpr std::size_t WORD_BYTES = 3;
    static constexpr std::size_t FRAME_WORDS = NUM_CHANNELS + 2;
    static constexpr std::size_t FRAME_BYTES = FRAME_WORDS * WORD_BYTES;

    // Full-scale range is +/- VREF / gain, where VREF is either the
    // internal 1.2 V reference or 0.96 * the voltage on REFIN.
    static constexpr float INTERNAL_VREF = 1.2f;
    static constexpr float EXTERNAL_REF_SCALE = 0.96f;

    // Commands
    static constexpr uint16_t CMD_NULL = 0x0000;
    static constexpr uint16_t CMD_RESET = 0x0011;
    static constexpr uint16_t CMD_STANDBY = 0x0022;
    static constexpr uint16_t CMD_WAKEUP = 0x0033;

    // Expected response to RESET for the 8-channel device.
    static constexpr uint16_t RESET_RESPONSE = 0xFF28;

    // Registers
    static constexpr uint8_t REG_ID = 0x00;
    static constexpr uint8_t REG_STATUS = 0x01;
    static constexpr uint8_t REG_MODE = 0x02;
    static constexpr uint8_t REG_CLOCK = 0x03;
    static constexpr uint8_t REG_GAIN1 = 0x04;
    static constexpr uint8_t REG_GAIN2 = 0x05;
    static constexpr uint8_t REG_CFG = 0x06;

    // CLOCK register bits
    static constexpr uint16_t CLOCK_XTAL_DIS = 0x0080;
    static constexpr uint16_t CLOCK_EXTREF_EN = 0x0040;

    // Oversampling ratio. Output data rate = (CLKIN / 2) / OSR,
    // e.g. 4.096 MHz CLKIN with OSR 4096 gives 500 SPS.
    enum class OSR : uint8_t
    {
        OSR_128 = 0,
        OSR_256 = 1,
        OSR_512 = 2,
        OSR_1024 = 3,
        OSR_2048 = 4,
        OSR_4096 = 5,
        OSR_8192 = 6,
        OSR_16256 = 7
    };

    // Modulator bias setting (CLOCK PWR bits). The datasheet specifies
    // each mode at its own CLKIN: high resolution at 8.192 MHz,
    // low power at 4.096 MHz and very low power at 2.048 MHz.
    enum class PowerMode : uint8_t
    {
        VERY_LOW_POWER = 0,
        LOW_POWER = 1,
        HIGH_RESOLUTION = 2
    };

    struct Frame
    {
        // Response word. For a NULL command this is the STATUS register.
        uint16_t response = 0;

        // Raw signed 24-bit conversion results.
        std::array<int32_t, NUM_CHANNELS> codes{};

        bool crcValid = false;
    };

    explicit ADS131M08(SPIBus& bus);

    // Software reset. Returns true if the device answered with 0xFF28.
    bool reset();

    bool readRegister(uint8_t address, uint16_t& value);
    bool writeRegister(uint8_t address, uint16_t value);

    // gain must be a power of two between 1 and 128.
    bool setChannelGain(int channel, uint8_t gain);

    // Enables all channels and sets the OSR and power mode.
    bool setOversampling(OSR osr, PowerMode power);

    // Selects the voltage on REFIN (EXTREF_EN, CLOCK bit 6) instead of the
    // internal reference. The summary register map (Table 8-12) shows this
    // bit as reserved while the CLOCK register description (Table 8-17)
    // defines it, so the register is read back: `applied` reports whether
    // the bit actually changed.
    bool setExternalReference(bool enabled, bool& applied);

    // Turns the crystal oscillator circuit off (XTAL_DIS). Do this when
    // CLKIN is driven by an external clock.
    bool setCrystalOscillator(bool enabled);

    // Global-chop mode removes most of the PGA offset and offset drift,
    // at the cost of a lower effective data rate.
    bool setGlobalChop(bool enabled);

    // Clocks out one full frame using the NULL command. frame.response
    // holds STATUS, provided the previous frame was also a NULL.
    bool readFrame(Frame& frame);

    // Output data rate in samples per second for a given CLKIN frequency.
    static double dataRateHz(uint32_t clkinHz, OSR osr);

    // Reference voltage the ADC uses for conversions.
    static float effectiveReference(bool externalReference, float refinVolts);

    // Converts a raw code to the differential input voltage in volts.
    static float codeToVolts(
        int32_t code,
        uint8_t gain,
        float vref = INTERNAL_VREF
    );

    // True if the code is at either end of the 24-bit range.
    static bool isSaturated(int32_t code);

    // CRC-16-CCITT (polynomial 0x1021), as used by the device by default.
    static uint16_t crc16(
        const uint8_t* data,
        std::size_t length,
        uint16_t seed = 0xFFFF
    );

    static bool isValidGain(uint8_t gain);

private:
    SPIBus& bus;

    // Sends a command (and optional register data) in one frame.
    bool transferFrame(
        uint16_t command,
        const std::vector<uint16_t>& data,
        Frame* out
    );

    // Sends a command, then a NULL frame, and returns the response word
    // that the device sent back in the NULL frame.
    bool sendCommand(
        uint16_t command,
        const std::vector<uint16_t>& data,
        uint16_t& response
    );

    static int32_t signExtend24(uint32_t raw);
};
