#!/bin/bash

SERVICE_DIR=$HOME/.config/systemd/user
DAS_DIR=$(dirname $(cd $(dirname "${BASH_SOURCE[0]}") && pwd))

LOGGER_SERVICE_FILE=logger.service
ANT_PLUS_SERVICE_FILE=ant-plus.service

# Create folder for service if it doesn't yet exist
mkdir -p $SERVICE_DIR
echo "✓ Successfully created $SERVICE_DIR"

# Copy service files to service directory
cp $DAS_DIR/service/$LOGGER_SERVICE_FILE $SERVICE_DIR
cp $DAS_DIR/service/$ANT_PLUS_SERVICE_FILE $SERVICE_DIR
echo "✓ Coppied service files to $SERVICE_DIR"

# Append working directory to end of service file
echo WorkingDirectory=$DAS_DIR/DAS/das >> $SERVICE_DIR/$LOGGER_SERVICE_FILE
echo WorkingDirectory=$DAS_DIR/ant_plus_sensor >> $SERVICE_DIR/$ANT_PLUS_SERVICE_FILE
echo "✓ Appended working directory to $SERVICE_DIR"

# Point user towards README for further setup
echo ""
echo "- View README.md for more information on how to run the installed service"
echo ""
