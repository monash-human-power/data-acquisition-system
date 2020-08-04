#pragma once

#include <functional>
#include <thread>
#include <vector>

#include <ZetaRf.hpp>

#include "frame.hpp"
#include "thread_queue.hpp"
#include "rf_config/si4455_revb1_bidir_fixed_crc_pre10_sync3MHP_pay8_433mhz_40kbps.hpp"

class ZetaRfRadio
{
public:
    using ptr_t = std::shared_ptr<ZetaRfRadio>;

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

    ThreadQueue<Frame> send_queue_;

    std::function<void(Frame)> on_receive_;

    std::thread worker_;
    bool should_worker_join_ = false;

    void watch_send_queue();

    // Class is non-copyable
    ZetaRfRadio(const ZetaRfRadio& that) = delete;
    ZetaRfRadio& operator=(const ZetaRfRadio& that) = delete;
    
public:
    ZetaRfRadio();
    ~ZetaRfRadio();

    void set_on_received(std::function<void(Frame)> callback);
    void send_packets(const std::vector<Frame> frames);
};

using ZetaRfRadio_ptr = ZetaRfRadio::ptr_t;
