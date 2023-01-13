# Crash Alert

*This directory contains scripts to listen to the crash detection system and send alerts to subscribed users' devices when the bike crashes*


- [Crash Alert](#crash-alert)
  - [About](#about)
  - [Basic Setup and Usage](#basic-setup-and-usage)

## About
Upon receiving a true from the crash detection MQTT channel, the program sends an alert via this Slack channel in the MHP Slack workspace. This can be extended for more APIs by adding children of the MessageSender class and implementing the send_message() method with the APIs respective calls.

## Basic Setup and Usage
In the `crash_alert` directory, create `.env` file based on the `.env.example` file. 
To obtain the Slack API webhook URL you must be added as a collaborator on the MHP Crash Alert Slack App. The URL can be found by going to the [app's home page](https://api.slack.com/apps) and then using the sidebar links to go to `Incoming Webhooks > Webhook URLs for Your Workspace`. At the bottom of the page, there should be the webhook for the `#crash-alert` channel. 

These next steps assume that you have [poetry](https://python-poetry.org/) installed.

```bash
# Move into crash_alert directory
cd crash_alert

# Create a poetry environment using Python 3.7
poetry env use 3.7

# Enter the environment
poetry shell

# Install dependencies
poetry install
```

Run the main program with:
```bash
python main_crash_alert.py
```
This connects to the crash detection MQTT channel.

<br>
<br>

In another window, publish to the MQTT channel:
```bash
# to send a false
mosquitto_pub -t "/v3/wireless_module/3/crash_detection" -m '{"value": false}'

# to send a true
mosquitto_pub -t "/v3/wireless_module/3/crash_detection" -m '{"value": true}'
```
When a `true` is sent, a message should be sent in the Slack channel if it has been 10 seconds since the last `true` was received. When a `false` is received, no message should be sent.
<br/>