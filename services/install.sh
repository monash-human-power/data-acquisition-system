#!/bin/bash

SERVICE_DIR=$HOME/.config/systemd/user
DAS_DIR=$(dirname $(cd $(dirname "${BASH_SOURCE[0]}") && pwd))

LOGGER_SERVICE_FILE=logger.service
ANT_PLUS_SERVICE_FILE=ant-plus.service
CHASE_TX_SERVICE_FILE=chase_tx_mqtt.service
CHASE_RX_SERVICE_FILE=chase_rx_mqtt.service
CRASH_ALERT_SERVICE_FILE=crash_alert.service
LOG_TO_EXCEL_SERVICE_FILE=log-to-excel.service

# Create folder for service if it doesn't yet exist
mkdir -p $SERVICE_DIR
echo "✓ Successfully created $SERVICE_DIR"

# Copy service files to service directory
cp $DAS_DIR/services/$LOGGER_SERVICE_FILE $SERVICE_DIR
cp $DAS_DIR/services/$ANT_PLUS_SERVICE_FILE $SERVICE_DIR
cp $DAS_DIR/services/$CHASE_TX_SERVICE_FILE $SERVICE_DIR
cp $DAS_DIR/services/$CHASE_RX_SERVICE_FILE $SERVICE_DIR
cp $DAS_DIR/services/$CRASH_ALERT_SERVICE_FILE $SERVICE_DIR
cp $DAS_DIR/services/$LOG_TO_EXCEL_SERVICE_FILE $SERVICE_DIR
echo "✓ Coppied service files to $SERVICE_DIR"

# Append working directory to end of service file
echo WorkingDirectory=$DAS_DIR/DAS/das >> $SERVICE_DIR/$LOGGER_SERVICE_FILE
echo WorkingDirectory=$DAS_DIR/ant_plus_sensor >> $SERVICE_DIR/$ANT_PLUS_SERVICE_FILE
echo WorkingDirectory=$DAS_DIR/Bridge >> $SERVICE_DIR/$CHASE_TX_SERVICE_FILE
echo WorkingDirectory=$DAS_DIR/Bridge >> $SERVICE_DIR/$CHASE_RX_SERVICE_FILE
echo WorkingDirectory=$DAS_DIR/crash_alert >> $SERVICE_DIR/$CRASH_ALERT_SERVICE_FILE
echo WorkingDirectory=$DAS_DIR/DAS/das >> $SERVICE_DIR/$LOG_TO_EXCEL_SERVICE_FILE
echo "✓ Appended working directory to $SERVICE_DIR"

# Point user towards README for further setup
echo ""
echo "- View README.md for more information on how to run the installed service"
echo ""
