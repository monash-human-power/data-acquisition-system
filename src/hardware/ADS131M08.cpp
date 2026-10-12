#include "ADS131M08.h"

#include <chrono>
#include <iostream>
#include <thread>

namespace
{
    uint16_t rregCommand(uint8_t address)
    {
        // 101a aaaa annn nnnn, n = number of registers - 1
        return static_cast<uint16_t>(0xA000 | ((address & 0x3F) << 7));
    }

    uint16_t wregCommand(uint8_t address)
    {
        // 011a aaaa annn nnnn, n = number of registers - 1
        return static_cast<uint16_t>(0x6000 | ((address & 0x3F) << 7));
    }

    uint16_t wregResponse(uint8_t address)
    {
        // 010a aaaa ammm mmmm, m = number of registers written - 1
        return static_cast<uint16_t>(0x4000 | ((address & 0x3F) << 7));
    }

    uint8_t gainToCode(uint8_t gain)
    {
        uint8_t code = 0;

        while ((1u << code) < gain)
        {
            code++;
        }

        return code;
    }
}

ADS131M08::ADS131M08(SPIBus& bus)
    : bus(bus)
{
}

bool ADS131M08::reset()
{
    Frame ignored;

    if (!transferFrame(CMD_RESET, {}, &ignored))
    {
        return false;
    }

    // Allow the device to complete its reset before the next frame.
    std::this_thread::sleep_for(std::chrono::milliseconds(5));

    Frame response;

    if (!transferFrame(CMD_NULL, {}, &response))
    {
        return false;
    }

    if (response.response != RESET_RESPONSE)
    {
        std::cerr
            << "ADS131M08: unexpected reset response 0x"
            << std::hex << response.response
            << ", expected 0x" << RESET_RESPONSE
            << std::dec << std::endl;

        return false;
    }

    return true;
}

bool ADS131M08::readRegister(uint8_t address, uint16_t& value)
{
    return sendCommand(rregCommand(address), {}, value);
}

bool ADS131M08::writeRegister(uint8_t address, uint16_t value)
{
    uint16_t response = 0;

    if (!sendCommand(wregCommand(address), {value}, response))
    {
        return false;
    }

    if (response != wregResponse(address))
    {
        std::cerr
            << "ADS131M08: write to register 0x"
            << std::hex << static_cast<int>(address)
            << " not acknowledged (response 0x" << response << ")"
            << std::dec << std::endl;

        return false;
    }

    return true;
}

bool ADS131M08::setChannelGain(int channel, uint8_t gain)
{
    if (channel < 0 || channel >= NUM_CHANNELS || !isValidGain(gain))
    {
        return false;
    }

    // GAIN1 holds channels 0-3, GAIN2 holds channels 4-7.
    // Each channel uses 3 bits, spaced 4 bits apart.
    uint8_t address = (channel < 4) ? REG_GAIN1 : REG_GAIN2;
    int shift = (channel % 4) * 4;

    uint16_t value = 0;

    if (!readRegister(address, value))
    {
        return false;
    }

    value = static_cast<uint16_t>(value & ~(0x7 << shift));
    value = static_cast<uint16_t>(value | (gainToCode(gain) << shift));

    return writeRegister(address, value);
}

bool ADS131M08::setOversampling(OSR osr, PowerMode power)
{
    uint16_t value = 0;

    if (!readRegister(REG_CLOCK, value))
    {
        return false;
    }

    // CH7_EN..CH0_EN = 1, OSR in bits 4:2, PWR in bits 1:0.
    // Bits 7:5 are kept.
    value = static_cast<uint16_t>(
        (value & 0x00E0)
        | 0xFF00
        | ((static_cast<uint8_t>(osr) & 0x7) << 2)
        | (static_cast<uint8_t>(power) & 0x3)
    );

    return writeRegister(REG_CLOCK, value);
}

bool ADS131M08::setExternalReference(bool enabled, bool& applied)
{
    applied = false;

    uint16_t value = 0;

    if (!readRegister(REG_CLOCK, value))
    {
        return false;
    }

    if (enabled)
    {
        value = static_cast<uint16_t>(value | CLOCK_EXTREF_EN);
    }
    else
    {
        value = static_cast<uint16_t>(value & ~CLOCK_EXTREF_EN);
    }

    if (!writeRegister(REG_CLOCK, value))
    {
        return false;
    }

    uint16_t readBack = 0;

    if (!readRegister(REG_CLOCK, readBack))
    {
        return false;
    }

    applied = ((readBack & CLOCK_EXTREF_EN) != 0) == enabled;

    return true;
}

bool ADS131M08::setCrystalOscillator(bool enabled)
{
    uint16_t value = 0;

    if (!readRegister(REG_CLOCK, value))
    {
        return false;
    }

    if (enabled)
    {
        value = static_cast<uint16_t>(value & ~CLOCK_XTAL_DIS);
    }
    else
    {
        value = static_cast<uint16_t>(value | CLOCK_XTAL_DIS);
    }

    return writeRegister(REG_CLOCK, value);
}

bool ADS131M08::setGlobalChop(bool enabled)
{
    uint16_t value = 0;

    if (!readRegister(REG_CFG, value))
    {
        return false;
    }

    // GC_EN is bit 8
    if (enabled)
    {
        value = static_cast<uint16_t>(value | 0x0100);
    }
    else
    {
        value = static_cast<uint16_t>(value & ~0x0100);
    }

    return writeRegister(REG_CFG, value);
}

bool ADS131M08::readFrame(Frame& frame)
{
    return transferFrame(CMD_NULL, {}, &frame);
}

double ADS131M08::dataRateHz(uint32_t clkinHz, OSR osr)
{
    static constexpr uint32_t ratios[] = {
        128, 256, 512, 1024, 2048, 4096, 8192, 16256
    };

    // The modulator runs at CLKIN / 2
    return (clkinHz / 2.0) / ratios[static_cast<uint8_t>(osr) & 0x7];
}

float ADS131M08::effectiveReference(bool externalReference, float refinVolts)
{
    return externalReference
        ? EXTERNAL_REF_SCALE * refinVolts
        : INTERNAL_VREF;
}

float ADS131M08::codeToVolts(int32_t code, uint8_t gain, float vref)
{
    // 1 LSB = (2 * VREF / gain) / 2^24 = VREF / (gain * 2^23)
    return static_cast<float>(code) * vref
        / (static_cast<float>(gain) * 8388608.0f);
}

bool ADS131M08::isSaturated(int32_t code)
{
    return code >= 0x7FFFFF || code <= -0x800000;
}

uint16_t ADS131M08::crc16(
    const uint8_t* data,
    std::size_t length,
    uint16_t seed)
{
    uint16_t crc = seed;

    for (std::size_t i = 0; i < length; ++i)
    {
        crc = static_cast<uint16_t>(crc ^ (data[i] << 8));

        for (int bit = 0; bit < 8; ++bit)
        {
            if (crc & 0x8000)
            {
                crc = static_cast<uint16_t>((crc << 1) ^ 0x1021);
            }
            else
            {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }

    return crc;
}

bool ADS131M08::isValidGain(uint8_t gain)
{
    return gain != 0 && gain <= 128 && (gain & (gain - 1)) == 0;
}

bool ADS131M08::transferFrame(
    uint16_t command,
    const std::vector<uint16_t>& data,
    Frame* out)
{
    if (data.size() > NUM_CHANNELS)
    {
        return false;
    }

    // 16-bit values are MSB-aligned in each 24-bit word, followed by
    // a zero padding byte. Input CRC is disabled, so no CRC word is sent.
    std::vector<uint8_t> tx(FRAME_BYTES, 0);

    tx[0] = static_cast<uint8_t>(command >> 8);
    tx[1] = static_cast<uint8_t>(command & 0xFF);

    for (std::size_t i = 0; i < data.size(); ++i)
    {
        std::size_t offset = (i + 1) * WORD_BYTES;

        tx[offset] = static_cast<uint8_t>(data[i] >> 8);
        tx[offset + 1] = static_cast<uint8_t>(data[i] & 0xFF);
    }

    std::vector<uint8_t> rx;

    if (!bus.transfer(tx, rx) || rx.size() != FRAME_BYTES)
    {
        return false;
    }

    if (out == nullptr)
    {
        return true;
    }

    out->response = static_cast<uint16_t>((rx[0] << 8) | rx[1]);

    for (int ch = 0; ch < NUM_CHANNELS; ++ch)
    {
        std::size_t offset = (ch + 1) * WORD_BYTES;

        uint32_t raw =
            (static_cast<uint32_t>(rx[offset]) << 16)
            | (static_cast<uint32_t>(rx[offset + 1]) << 8)
            | static_cast<uint32_t>(rx[offset + 2]);

        out->codes[ch] = signExtend24(raw);
    }

    // The output CRC covers every word before the CRC word,
    // including padding bytes.
    std::size_t crcOffset = (FRAME_WORDS - 1) * WORD_BYTES;

    uint16_t receivedCrc =
        static_cast<uint16_t>((rx[crcOffset] << 8) | rx[crcOffset + 1]);

    out->crcValid = crc16(rx.data(), crcOffset) == receivedCrc;

    return true;
}

bool ADS131M08::sendCommand(
    uint16_t command,
    const std::vector<uint16_t>& data,
    uint16_t& response)
{
    if (!transferFrame(command, data, nullptr))
    {
        return false;
    }

    Frame frame;

    if (!transferFrame(CMD_NULL, {}, &frame))
    {
        return false;
    }

    if (!frame.crcValid)
    {
        std::cerr << "ADS131M08: CRC error in command response" << std::endl;
        return false;
    }

    response = frame.response;

    return true;
}

int32_t ADS131M08::signExtend24(uint32_t raw)
{
    if (raw & 0x800000)
    {
        return static_cast<int32_t>(raw | 0xFF000000u);
    }

    return static_cast<int32_t>(raw);
}
