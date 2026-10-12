#include "StrainGaugeSensor.h"

#include <chrono>
#include <iostream>
#include <thread>

namespace
{
    // MODE register: 24-bit words, SPI timeout enabled, RESET flag cleared
    constexpr uint16_t MODE_CONFIG = 0x0110;

    // Conversions thrown away after configuring, while the
    // sinc3 digital filter settles
    constexpr int SETTLING_SAMPLES = 4;

    std::uint64_t currentTimestampMs()
    {
        return static_cast<std::uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );
    }
}

StrainGaugeSensor::StrainGaugeSensor(
    std::string id,
    SPIBus& sharedBus,
    std::vector<StrainChannelConfig> channels,
    StrainGaugeADCSettings settings,
    GPIOInput* drdy)
    : SPISensor(id, sharedBus),
      adc(sharedBus),
      channels(std::move(channels)),
      settings(settings),
      vref(ADS131M08::INTERNAL_VREF),
      drdy(drdy),
      useDrdy(false),
      externalReferenceActive(false),
      initialised(false),
      channelMask(0)
{
    for (const StrainChannelConfig& config : this->channels)
    {
        if (config.channel >= 0 && config.channel < ADS131M08::NUM_CHANNELS)
        {
            channelMask = static_cast<uint16_t>(channelMask | (1u << config.channel));
        }
    }

    lastReading.sensorID = sensorID;
    lastReading.timestamp = 0;
    lastReading.values.clear();
    lastReading.isValid = false;
}

bool StrainGaugeSensor::init()
{
    initialised = false;

    if (!validateConfig())
    {
        return false;
    }

    if (!bus.isOpen() && !bus.openBus())
    {
        return false;
    }

    useDrdy = false;

    if (drdy != nullptr)
    {
        useDrdy = drdy->isOpen() || drdy->openLine();

        if (!useDrdy)
        {
            std::cerr
                << sensorID
                << ": warning: DRDY pin unavailable, polling STATUS instead"
                << std::endl;
        }
    }

    if (!adc.reset())
    {
        std::cerr << sensorID << ": ADS131M08 did not respond to reset" << std::endl;
        return false;
    }

    uint16_t id = 0;

    if (!adc.readRegister(ADS131M08::REG_ID, id))
    {
        std::cerr << sensorID << ": could not read ADS131M08 ID" << std::endl;
        return false;
    }

    // ID bits 11:8 hold the channel count
    if (((id >> 8) & 0x0F) != ADS131M08::NUM_CHANNELS)
    {
        std::cerr
            << sensorID
            << ": unexpected ID 0x" << std::hex << id << std::dec
            << ", expected an 8-channel ADS131M08"
            << std::endl;

        return false;
    }

    if (!adc.writeRegister(ADS131M08::REG_MODE, MODE_CONFIG) ||
        !adc.setOversampling(settings.osr, settings.powerMode) ||
        !adc.setCrystalOscillator(false))
    {
        std::cerr << sensorID << ": failed to configure ADS131M08" << std::endl;
        return false;
    }

    externalReferenceActive = false;

    if (settings.externalReference)
    {
        if (!adc.setExternalReference(true, externalReferenceActive))
        {
            std::cerr << sensorID << ": failed to configure ADS131M08 reference" << std::endl;
            return false;
        }

        if (!externalReferenceActive)
        {
            std::cerr
                << sensorID
                << ": warning: EXTREF_EN did not set, using the internal 1.2 V reference"
                << std::endl;
        }
    }

    vref = ADS131M08::effectiveReference(externalReferenceActive, settings.refinVolts);

    for (const StrainChannelConfig& config : channels)
    {
        if (!adc.setChannelGain(config.channel, config.pgaGain))
        {
            std::cerr
                << sensorID
                << ": failed to set gain for channel "
                << config.channel
                << std::endl;

            return false;
        }
    }

    if (settings.globalChop && !adc.setGlobalChop(true))
    {
        std::cerr << sensorID << ": failed to enable global chop" << std::endl;
        return false;
    }

    std::array<double, ADS131M08::NUM_CHANNELS> discarded{};
    bool saturated = false;

    if (!acquire(SETTLING_SAMPLES, discarded, saturated))
    {
        std::cerr << sensorID << ": ADS131M08 is not producing data" << std::endl;
        return false;
    }

    offsetVolts.fill(0.0);
    initialised = true;

    std::cout
        << sensorID
        << ": ADS131M08 initialised with "
        << channels.size()
        << " strain channel(s)"
        << (useDrdy ? ", using DRDY" : ", polling STATUS")
        << (externalReferenceActive ? ", external reference" : ", internal reference")
        << std::endl;

    return true;
}

bool StrainGaugeSensor::read()
{
    lastReading.sensorID = sensorID;
    lastReading.timestamp = currentTimestampMs();

    std::array<double, ADS131M08::NUM_CHANNELS> volts{};
    bool saturated = false;

    if (!initialised || !acquire(settings.samplesPerReading, volts, saturated))
    {
        lastReading.values.clear();
        lastReading.isValid = false;

        return false;
    }

    lastReading.values.clear();

    for (const StrainChannelConfig& config : channels)
    {
        double bridgeVolts = volts[config.channel];

        double ratio =
            (bridgeVolts - offsetVolts[config.channel])
            / config.excitationVoltage;

        double strain = ratio / (config.gaugeFactor * config.bridgeFactor);

        lastReading.values[config.name + "_microstrain"] =
            static_cast<float>(strain * 1.0e6);

        lastReading.values[config.name + "_mv"] =
            static_cast<float>(bridgeVolts * 1000.0);
    }

    // A clipped input means the strain value cannot be trusted.
    // Lower the PGA gain if this happens.
    lastReading.isValid = !saturated;

    return true;
}

bool StrainGaugeSensor::tare(int samples)
{
    if (!initialised)
    {
        return false;
    }

    std::cout << sensorID << ": taring strain gauges..." << std::endl;

    std::array<double, ADS131M08::NUM_CHANNELS> volts{};
    bool saturated = false;

    if (!acquire(samples, volts, saturated))
    {
        std::cerr << sensorID << ": tare failed" << std::endl;
        return false;
    }

    if (saturated)
    {
        std::cerr
            << sensorID
            << ": tare failed, an input is saturated (reduce the PGA gain)"
            << std::endl;

        return false;
    }

    offsetVolts = volts;

    for (const StrainChannelConfig& config : channels)
    {
        std::cout
            << "  " << config.name
            << " offset: " << offsetVolts[config.channel] * 1000.0
            << " mV"
            << std::endl;
    }

    return true;
}

bool StrainGaugeSensor::isInitialised() const
{
    return initialised;
}

bool StrainGaugeSensor::isUsingDrdy() const
{
    return useDrdy;
}

bool StrainGaugeSensor::isUsingExternalReference() const
{
    return externalReferenceActive;
}

bool StrainGaugeSensor::acquire(
    int samples,
    std::array<double, ADS131M08::NUM_CHANNELS>& averageVolts,
    bool& saturated)
{
    std::array<double, ADS131M08::NUM_CHANNELS> sums{};
    saturated = false;

    int collected = 0;
    int crcErrors = 0;

    // Allow twice the expected conversion time, plus margin for
    // scheduling delays.
    double samplePeriodMs = 1000.0 / ADS131M08::dataRateHz(settings.clockHz, settings.osr);

    auto deadline =
        std::chrono::steady_clock::now()
        + std::chrono::milliseconds(
            static_cast<int>(samples * samplePeriodMs * 2.0) + 50
        );

    // Edges from conversions since the last read are stale. Wait for the
    // next conversion instead.
    if (useDrdy)
    {
        drdy->discardEdges();
    }

    // The ADC buffers two samples per channel. After a gap in reading,
    // both are full and old, so read two frames to empty the buffer
    // (datasheet 8.5.1.9.1). This comes after discarding edges, so a
    // conversion completing in between still produces an edge to wait for.
    for (int i = 0; i < 2; ++i)
    {
        ADS131M08::Frame stale;

        if (!adc.readFrame(stale))
        {
            return false;
        }
    }

    while (collected < samples && std::chrono::steady_clock::now() < deadline)
    {
        if (useDrdy)
        {
            auto remaining =
                std::chrono::duration_cast<std::chrono::milliseconds>(
                    deadline - std::chrono::steady_clock::now()
                ).count();

            int edge = drdy->waitForFallingEdge(
                static_cast<int>(remaining > 0 ? remaining : 0) + 1
            );

            if (edge < 0)
            {
                std::cerr << sensorID << ": error waiting for DRDY" << std::endl;
                return false;
            }

            if (edge == 0)
            {
                break;
            }
        }

        ADS131M08::Frame frame;

        if (!adc.readFrame(frame))
        {
            return false;
        }

        if (!frame.crcValid)
        {
            if (++crcErrors > samples)
            {
                std::cerr << sensorID << ": too many SPI CRC errors" << std::endl;
                return false;
            }

            continue;
        }

        // STATUS bits 7:0 are DRDY7..DRDY0. With the DRDY pin these are
        // already set; this also skips a DRDY glitch.
        if ((frame.response & channelMask) != channelMask)
        {
            if (!useDrdy)
            {
                std::this_thread::sleep_for(std::chrono::microseconds(100));
            }

            continue;
        }

        for (const StrainChannelConfig& config : channels)
        {
            int32_t code = frame.codes[config.channel];

            if (ADS131M08::isSaturated(code))
            {
                saturated = true;
            }

            sums[config.channel] += ADS131M08::codeToVolts(code, config.pgaGain, vref);
        }

        collected++;
    }

    if (collected < samples)
    {
        std::cerr
            << sensorID
            << ": timed out waiting for ADS131M08 data (check CLKIN"
            << (useDrdy ? " and the DRDY wiring)" : ")")
            << std::endl;

        return false;
    }

    for (std::size_t ch = 0; ch < sums.size(); ++ch)
    {
        averageVolts[ch] = sums[ch] / collected;
    }

    return true;
}

bool StrainGaugeSensor::validateConfig() const
{
    if (channels.empty())
    {
        std::cerr << sensorID << ": no strain channels configured" << std::endl;
        return false;
    }

    if (settings.clockHz == 0)
    {
        std::cerr << sensorID << ": clockHz must be set" << std::endl;
        return false;
    }

    // The ADS131M08 accepts 1.1 V to 1.3 V on REFIN
    if (settings.externalReference &&
        (settings.refinVolts < 1.1f || settings.refinVolts > 1.3f))
    {
        std::cerr << sensorID << ": refinVolts must be between 1.1 V and 1.3 V" << std::endl;
        return false;
    }

    if (settings.samplesPerReading < 1)
    {
        std::cerr << sensorID << ": samplesPerReading must be at least 1" << std::endl;
        return false;
    }

    uint16_t seen = 0;

    for (const StrainChannelConfig& config : channels)
    {
        bool valid =
            config.channel >= 0
            && config.channel < ADS131M08::NUM_CHANNELS
            && !(seen & (1u << config.channel))
            && ADS131M08::isValidGain(config.pgaGain)
            && config.gaugeFactor != 0.0f
            && config.bridgeFactor != 0.0f
            && config.excitationVoltage > 0.0f
            && !config.name.empty();

        if (!valid)
        {
            std::cerr
                << sensorID
                << ": invalid configuration for strain channel '"
                << config.name << "'"
                << std::endl;

            return false;
        }

        seen = static_cast<uint16_t>(seen | (1u << config.channel));
    }

    return true;
}
