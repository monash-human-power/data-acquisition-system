#pragma once

#include <iostream>

extern "C" {
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "esp_twai.h"
#include "esp_twai_onchip.h"
#include "esp_timer.h"
#include "esp_log.h"
}

using namespace std;

class TwaiNode {
    private:
        twai_node_handle_t nodeHdl;
        static bool tx_callback(twai_node_handle_t handle, const twai_tx_done_event_data_t* edata, void* user_ctx);
        static bool rx_callback(twai_node_handle_t handle, const twai_rx_done_event_data_t* edata, void* user_ctx);
        static bool err_callback(twai_node_handle_t handle, const twai_error_event_data_t* edata, void* user_ctx);

    public:
        TwaiNode(gpio_num_t txPin, gpio_num_t rxPin, unsigned long bitrate, int txQueueDepth);
        ~TwaiNode();
        // void configure_mask(uint32_t id, uint32_t mask);
        void register_event_callbacks();
        void configure_timing(uint32_t prescalar=40,uint8_t propSeg=0, uint8_t tseg1=11, uint8_t tseg2=4, uint8_t sjw=1);
        void enable_node();
        void send_message(twai_frame_t& frame);
        twai_node_handle_t get_handle();
    protected:

};

