#pragma once

#include <functional>
#include <vector>

#include <ZetaRf.hpp>

#include "frame.hpp"
#include "thread_queue.hpp"
#include "rf_config/si4455_revb1_bidir_fixed_crc_pre10_sync3MHP_pay8_433mhz_40kbps.hpp"

class ZetaRfRadio
{
private:
    using RadioConfig = Config433_FixedLength_CRC_Preamble10_Sync3MHP_Payload8_40kbps;

    using SpiChipSelectPin = ZetaRf::CS<6>;
    using ShutdownPin = ZetaRf::SDN<9>;
    using InteruptRequestPin = ZetaRf::IRQ<8>;

    constexpr static uint8_t ZETA_CHANNEL = 4;

    ZetaRfConfig<RadioConfig, ZetaRfEZRadio::EZRadioSi4455<SpiHal<
        SpiChipSelectPin,
        ShutdownPin,
        InteruptRequestPin
    >>> zeta_;
    
public:
    ZetaRfRadio();

    void send_packets(std::vector<Frame>);
    void setOnReceived(std::function<void(Frame)> callback);
};
