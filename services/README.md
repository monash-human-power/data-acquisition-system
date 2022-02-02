# Systemd files

This folder contains scripts needed to create our own systemd unit service for DAS related processes.

This allows us to start DAS logger (etc.) when our Raspberry Pi boots up and be able to restart the script if the logger crashes.

Currently, the services we have are:

- `logger.service`: The MQTT logger which records all MQTT messages into a CSV file
- `ant-plus.service`: The pretend wireless module which gets ANT+ sensor data (power, cadence, HR) and publishes on MQTT.

## Usage

Run `install.sh` to add the service files to the `~/.config/systemd/user/` folder on the OS system.

Below, `logger.service` may be substituted with any other service file.

Enable (i.e. start automatically on boot) the unit by running:

```
systemctl --user enable logger.service
```

To manually start/stop the unit, run

```
systemctl --user <<start or stop>> logger.service
```

To view the latest logs for the unit use

```
journalctl _PID=<<pid of the unit>>
```

where the PID of the unit can be found using

```
systemctl --user status logger.service
```

Tip: Add the `-f` flag to continuously monitor new logs

## Requirements

For poetry to correctly clone the `common/mhp` repository using SSH, the public key of the Pi must me shared with a github account on the MHP organisation. In the case of deployments, use `mhp-deployment`.
