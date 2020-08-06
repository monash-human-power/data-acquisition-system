#pragma once

#include <functional>
#include <thread>
#include <vector>

#include <ZetaRf.hpp>

#include "frame.hpp"
#include "thread_queue.hpp"
#include "rf_config/si4455_revb1_bidir_fixed_crc_pre10_sync3MHP_pay8_433mhz_40kbps.hpp"

/**
 * Class to handle all communication with the ZetaRF radio module.
 * 
 * Once initialised, the class will listen for new packets and process outgoing
 * messages in a background thread. This thead will be terminated on
 * destruction of the class.
 */
class ZetaRfRadio
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
        InteruptRequestPin
    >>> zeta_;

    /** Queue of packets which have not yet been transmitted. */
    ThreadQueue<Frame> send_queue_;

    /** Callback which is called when a packet is successfully received. */
    std::function<void(Frame)> on_receive_;

    /** Background thread which receives/transmits packets after initialisation. */
    std::thread worker_;
    /** Specifies if the worker thread should stop. */
    bool should_worker_join_ = false;

    /**
     * Start a loop which repeatedly checks for received packets (which are
     * then processed) and check for queued packets to be sent (which are will
     * then sent). The loop will run until `this->should_worker_join` is true.
     */
    void rx_tx_loop();
    /** Update the ZetaRF library and process any events that occur. */
    void process_zeta_events();
    /**
     * Read a packet from the Zeta module's rx fifo and if successful, pass
     * the packet to the `on_received_` callback.
     */
    void read_packet();
    /**
     * Transmit a packet using the Zeta radio module.
     * @param packet The Frame to be sent.
     */
    void transmit_packet(const Frame packet);

    // Class is non-copyable
    ZetaRfRadio(const ZetaRfRadio& that) = delete;
    ZetaRfRadio& operator=(const ZetaRfRadio& that) = delete;
    
public:
    /**
     * Create a ZetaRfRadio which can be used to transmit and receive radio
     * messages.
     */
    ZetaRfRadio();
    /** Stop all background processors for the ZetaRfRadio */
    ~ZetaRfRadio();

    /**
     * Set the function to be called when a radio packet is received.
     * @param callback The function which accepts a Frame to be called.
     */
    void set_on_received(std::function<void(Frame)> callback);
    /**
     * Add a collection of packets/frames to the transmit queue.
     * @param frames The packets to be sent, in the order that they should be
     *               transmitted.
     */
    void send_packets(const std::vector<Frame> frames);
};

/** Smart/shared pointer to a ZetaRfRadio */
using ZetaRfRadio_ptr = ZetaRfRadio::ptr_t;
