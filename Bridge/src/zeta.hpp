#pragma once

#include <functional>
#include <vector>

#include <ZetaRf.hpp>

#include "radio.hpp"

// This can be replaced with any other config, but you must ensure both ends of
// the bridge use the same config. The configurations built in to the ZetaRf
// library will all work, or new configs may be made using the Silicon Labs
// WDS. (they will need minor modifications into the structs used by ZetaRf.)
//
// This current config uses 433 MHz, the sync word "MHP" and a theoretical
// bandwidth of 40 kbps.
#include "rf_config/si4455_revb1_bidir_fixed_crc_pre10_sync3MHP_pay8_433mhz_40kbps.hpp"

/**
 * Class to handle all communication with the ZetaRF radio module.
 *
 * Once initialised, the class will listen for new packets and process outgoing
 * messages in a background thread. This thead will be terminated on
 * destruction of the class.
 */
class ZetaRfRadio : public Radio
{
public:
    /** Smart/shared pointer to this class. */
    using ptr_t = std::shared_ptr<ZetaRfRadio>;

private:
    /**
     * The radio configuration for the Zeta module/ZetaRf library.
     * Currently specifies to operate on 433 MHz with a fixed 80 byte packet
     * size and the sync word "MHP", with a data rate of 40 kbps.
     */
    using RadioConfig = Config433_FixedLength_CRC_Preamble10_Sync3MHP_Payload8_40kbps;

    /** The wiringPi pins which connect the ZetaRf module to the Pi. */
    using SpiChipSelectPin = ZetaRf::CS<6>;
    using ShutdownPin = ZetaRf::SDN<9>;
    using InteruptRequestPin = ZetaRf::IRQ<8>;

    /** The Zeta radio channel to transmit/receive on. */
    constexpr static uint8_t ZETA_CHANNEL = 4;

    /**
     * The ZetaRfRadio's instance of the ZetaRf library.
     * All interfacing with the module is performed through this member.
     */
    ZetaRfConfig<RadioConfig, ZetaRfEZRadio::EZRadioSi4455<SpiHal<
                                  SpiChipSelectPin,
                                  ShutdownPin,
                                  InteruptRequestPin>>>
        zeta_;

    /**
     * Read a packet from the Zeta module's rx fifo and if successful, pass
     * the packet to the `on_received_` callback.
     */
    void read_packet();
    /**
     * Called in the rx_tx_loop. Performs any periodically required actions
     * (e.g. receiving packets).
     */
    void loop_tick();
    /**
     * Transmit a packet using the Zeta radio module.
     * @param packet The Frame to be sent.
     */
    void transmit_packet(const Frame packet);

public:
    /**
     * Create a ZetaRfRadio which can be used to transmit and receive radio
     * messages.
     */
    ZetaRfRadio();
};

/** Smart/shared pointer to a ZetaRfRadio */
using ZetaRfRadio_ptr = ZetaRfRadio::ptr_t;
