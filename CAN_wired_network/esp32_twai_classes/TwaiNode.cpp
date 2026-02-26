#include "TwaiNode.h"
#include <iostream>
static const char* TAG = "esp32_node";

using namespace std;

TwaiNode::TwaiNode(gpio_num_t txPin, gpio_num_t rxPin, unsigned long bitrate, int txQueueDepth) {
    twai_onchip_node_config_t node_config = {};
    node_config.io_cfg = {
        .tx = txPin,
        .rx = rxPin,
        .quanta_clk_out = GPIO_NUM_NC,
        .bus_off_indicator = GPIO_NUM_NC,
    };
    node_config.bit_timing = {
        .bitrate =  bitrate,
    };
    node_config.flags = {
        .enable_self_test = false,
    };
    node_config.fail_retry_cnt = 3;
    node_config.tx_queue_depth = txQueueDepth;
    ESP_ERROR_CHECK(twai_new_node_onchip(&node_config, &nodeHdl));
    ESP_LOGI(TAG,"Node started");
}

TwaiNode::~TwaiNode() {
    if (nodeHdl) {
        twai_node_disable(nodeHdl);
        twai_node_delete(nodeHdl);
    }
}

// void TwaiNode::configure_mask(uint32_t id, uint32_t mask) {
//     twai_mask_filter_config_t filter = {
//         .id = id,
//         .mask = mask,
//         .is_ext = false,
//     };
//     ESP_ERROR_CHECK(twai_node_config_mask_filter(nodeHdl,0,&filter));
//     ESP_LOGI(TAG, "Filter enabled for ID: 0x%03X Mask: 0x%03X", filter.id, filter.mask);
// }

void TwaiNode::register_event_callbacks() {
    twai_event_callbacks_t callbacks {
        .on_tx_done = tx_callback,
        .on_rx_done = rx_callback,
        .on_error = err_callback,
    };
    ESP_ERROR_CHECK(twai_node_register_event_callbacks(nodeHdl,&callbacks,this));
    ESP_LOGI(TAG,"callbacks registered");
}

bool TwaiNode::tx_callback(twai_node_handle_t handle, const twai_tx_done_event_data_t* edata, void* user_ctx) {
    // if(!edata->is_tx_success) {
    //     ESP_EARLY_LOGW(TAG,"Failed to transmit message, ID: 0x%X", edata->done_tx_frame->header.id);
    // } else {
    //     ESP_EARLY_LOGW(TAG,"message sent successfully");
    // }
    return false;
}

bool TwaiNode::rx_callback(twai_node_handle_t handle, const twai_rx_done_event_data_t* edata, void* user_ctx) {
    ESP_EARLY_LOGI(TAG, "receive callback triggered");
    uint8_t recv_buff[8];
    twai_frame_t rx_frame = {
        .buffer = recv_buff,
        .buffer_len = sizeof(recv_buff),
    };

    if (ESP_OK == twai_node_receive_from_isr(handle,&rx_frame)) {
        ESP_EARLY_LOGI(TAG,"Received msg: %lld",recv_buff);
    }
    return false;
}

bool TwaiNode::err_callback(twai_node_handle_t handle, const twai_error_event_data_t* edata, void* user_ctx) {
    ESP_EARLY_LOGW(TAG, "TWAI error: 0x%x", edata->err_flags.val);
    return false;
}

void TwaiNode::configure_timing(uint32_t prescalar,uint8_t propSeg, uint8_t tseg1, uint8_t tseg2, uint8_t sjw) {
    twai_timing_advanced_config_t timing_cfg = {
    .brp = prescalar,       // 80Mhz/40 = 2 Mhz = 500 ns per TQ
    .prop_seg = propSeg, // 0 because short bus length
    .tseg_1 = tseg1, // 75% sample point (synchronisation segment is 1 TQ)
    .tseg_2 = tseg2,
    .sjw = sjw,       // Synchronization Jump Width
    };
    ESP_ERROR_CHECK(twai_node_reconfig_timing(nodeHdl, &timing_cfg, NULL)); // Configure arbitration phase
    ESP_LOGI(TAG,"Timing configured");
}

void TwaiNode::enable_node() {
    ESP_ERROR_CHECK(twai_node_enable(nodeHdl));
    ESP_LOGI(TAG,"node started successfully");
};

void TwaiNode::send_message(twai_frame_t frame) {
    ESP_ERROR_CHECK(twai_node_transmit(nodeHdl,&frame,-1));
}

twai_node_handle_t TwaiNode::get_handle() {
    return nodeHdl;
}