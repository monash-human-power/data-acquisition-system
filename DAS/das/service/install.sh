#!/bin/bash

SERVICE_DIR=$HOME/.config/systemd/user
DAS_DIR=$(dirname $(cd $(dirname "${BASH_SOURCE[0]}") && pwd))
SERVICE_FILE=logger.service

echo SERVICE_FILE

# Create folder for service if it doesn't yet exist
mkdir -p $SERVICE_DIR

# Copy service files to service directory
cp $DAS_DIR/service/$SERVICE_FILE $SERVICE_DIR

# Append working directory to end of service file
echo WorkingDirectory=$DAS_DIR >> $SERVICE_DIR/$SERVICE_FILE