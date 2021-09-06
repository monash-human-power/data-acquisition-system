# Systemd files
This folder contains scripts needed to create our own systemd unit service for the DAS logger.

This allows us to start DAS logger when our Raspberry Pi boots up and be able to restart the script if the logger crashes.

## Usage
Run `install.sh` to add `logger.service` to the `~/.config/systemd/user/` folder on the OS system.

Enable the unit by running:
```
systemctl --user enable logger.service
```

To manually start/stop the unit, run
```
systemctl --user <<start or stop>> logger.service
```

The PID of the unit can be found using
```
systemctl --user status logger.service
```

To view the latest logs for the unit use
```
journalctl _PID=<<pid of the unit>>
```

Tip: Add the `-f` flag to continuously monitor new logs


## Requirements
For poetry to correctly clone the `common/mhp` repository using SSH, the public key of the Pi must me shared with our 
github account