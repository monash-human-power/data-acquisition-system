#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "esp_twai.h"
#include "esp_twai_onchip.h"
#include "esp_log.h"
#include "esp_timer.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

//constants
#define TAG "esp32_node"
#define TX_GPIO GPIO_NUM_17
#define RX_GPIO GPIO_NUM_18
#define BITRATE 1000000
#define TX_QUEUE_DEPTH 1
#define DATA_ID 0x0

//initialise semaphore for binary semaphore later
SemaphoreHandle_t tx_sem;

static bool IRAM_ATTR rx_success_callback(twai_node_handle_t handle, const twai_rx_done_event_data_t *edata, void *user_ctx){
    /*
    event callback for when esp32 received a CAN frame from the bus
    Inputs:
        handle: handle to the twai node
        edata: event data 
        user_ctx: data user wants to pass to this callback
    */

    //create frame for reception
    uint8_t recv_buff[8];
    twai_frame_t rx_frame = {
        .buffer = recv_buff,
        .buffer_len = sizeof(recv_buff),
    };

    //read received frame from rx queue into rx_frame
    if (ESP_OK == twai_node_receive_from_isr(handle,&rx_frame)) {
        for (int i = 0;i<8;i++) {
            ESP_EARLY_LOGI(TAG,"%dth byte: %X",i,recv_buff[i]);
        }
    }
    return false;
}   

static bool IRAM_ATTR error_callback(twai_node_handle_t handle,const twai_error_event_data_t *edata,void *user_ctx) {
    /*
    event callback for when error occurs
    Inputs:
        handle: handle to the twai node
        edata: event data 
        user_ctx: data user wants to pass to this callback
    **Not exactly sure what each error flag shows, just took this from official esp-idf example
    */
    ESP_EARLY_LOGW(TAG, "TWAI error: 0x%x", edata->err_flags.val);
    return false;
}

static bool IRAM_ATTR tx_success_callback(twai_node_handle_t handle,const twai_tx_done_event_data_t *edata, void *user_ctx) {
    /*
    event callback for when esp32 transmits a message
    Inputs:
        handle: handle to the twai node
        edata: event data 
        user_ctx: data user wants to pass to this callback
    */
    if(!edata->is_tx_success) {
        ESP_EARLY_LOGW(TAG,"Failed to transmit message, ID: 0x%X", edata->done_tx_frame->header.id);
    } else {
        //if successful transmission, i.e frame has left the queue and been sent to the bus, run below code
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        //Free code to put another message onto the queue
        xSemaphoreGiveFromISR(tx_sem, &xHigherPriorityTaskWoken);
        //yield this task if high priority task is required to run
        if (xHigherPriorityTaskWoken) {
            portYIELD_FROM_ISR();
        }   
    }
    return false;
}

void app_main(void) {

    // node config
    twai_node_handle_t node_hdl = NULL;
    twai_onchip_node_config_t node_config = {
        .io_cfg = {
            .tx = TX_GPIO,
            .rx = RX_GPIO,
            .quanta_clk_out = GPIO_NUM_NC,
            .bus_off_indicator = GPIO_NUM_NC,
        },
        .bit_timing = {
            .bitrate = BITRATE,
        },
        .flags = {
            .enable_self_test = false,
        },
        .fail_retry_cnt = 3,
        .tx_queue_depth = TX_QUEUE_DEPTH,
    };
    ESP_ERROR_CHECK(twai_new_node_onchip(&node_config, &node_hdl));

    //register event callbacks
    twai_event_callbacks_t callbacks = {
        .on_rx_done = rx_success_callback,
        .on_error = error_callback,
        .on_tx_done = tx_success_callback,
    };
    ESP_ERROR_CHECK(twai_node_register_event_callbacks(node_hdl,&callbacks,NULL));

    //create acceptance filter
    // twai_mask_filter_config_t filter = {
    //     .id = DATA_ID,
    //     .mask = 0x0,
    //     .is_ext = false,
    // };
    // ESP_ERROR_CHECK(twai_node_config_mask_filter(node_hdl,0,&filter));
    // ESP_LOGI(TAG, "Filter enabled for ID: 0x%03X Mask: 0x%03X", filter.id, filter.mask);

    // // create timing config
    // twai_timing_advanced_config_t timing_cfg = {
    // .brp = 40,       // 80Mhz/40 = 2 Mhz = 500 ns per TQ
    // .prop_seg = 0, // 0 because short bus length
    // .tseg_1 = 11, // 75% sample point (synchronisation segment is 1 TQ)
    // .tseg_2 = 4,
    // .sjw = 1,       // Synchronization Jump Width
    // };
    // ESP_ERROR_CHECK(twai_node_reconfig_timing(node_hdl, &timing_cfg, NULL)); // Configure arbitration phase

    //enable node
    ESP_ERROR_CHECK(twai_node_enable(node_hdl));
    ESP_LOGI(TAG,"node started successfully");

    //create binary semaphore so messages are only put into the queue after the previous message is put on the bus
    tx_sem = xSemaphoreCreateBinary();
    xSemaphoreGive(tx_sem);

    //create frame for transmission
    uint64_t sensorData = 0;
    twai_frame_t txFrame = {
        .buffer = (uint8_t *)&sensorData,
        .buffer_len = sizeof(sensorData),
        .header.id = DATA_ID
    };
    int64_t timeStart = esp_timer_get_time();
    //sent frame 10000 times, incrementing sensorData every time
    while (sensorData < 10000) {
        xSemaphoreTake(tx_sem,portMAX_DELAY);
        ESP_ERROR_CHECK(twai_node_transmit(node_hdl,&txFrame,-1));
        sensorData++;
    }
    //calculate time taken to send 10000 frames
    int64_t timeInterval = esp_timer_get_time() - timeStart;
    ESP_LOGI("TEST", "Sent %llu frames in %lld us", sensorData, timeInterval);

    //end twai node
    twai_node_disable(node_hdl);
    twai_node_delete(node_hdl); 

}