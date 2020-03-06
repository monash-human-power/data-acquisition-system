# Data Acquisition System

[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors)

The Data Acquisition System (DAS) allows us to collect and store data from various sensors attached to the bike.

## Getting Started

1. Type `git clone https://github.com/Monash-Human-Power/MHP_DAS.git` on the command line to download the whole repository.

## Contents

### Raspi

#### DAS.js

node.js program we run to communicate to the Teensy that is connected to the Raspberry Pi via serial communication.

### Test/mock_wireless_module.py

This script mocks module data over MQTT similar to the real sensors on V3.

#### Usage: Common use cases for mocking modules (All flags can be used with each other)

- Send data once per second for 5 seconds for modules 1, 2, 3 and 4
  - `python3 mock_wireless_module.py -t 5`
- Send data five times per second for a minute for modules 1, 2, 3 and 4
  - `python3 mock_wireless_module.py -t 60 -r 5`
- Send data once per second for modules 2, 5, and 1000 forever
  - `python3 mock_wireless_module.py -i 2 5 1000`
- Send data once per second for modules 1, 2, 3 and 4 for host on 192.168.1.100 forever
  - `python3 mock_wireless_module.py --host 192.168.1.100`

### Test/mqtt_wireless_log.py

Once started this script will log any data coming in on the MQTT module data and battery channels. The saved csv files will be in the format `module_id + _D%d-%m-%d_T%H-%M-%S + .csv`, where the date and time is the time when the start topic gets data sent on it.

#### Usage: Just start the script and data will be auto logged

- General use with the default MQTT broker set to localhost
  - `python3 mqtt_wireless_log.py`
- Same logger with the MQTT broker set to 192.168.1.100
  - `python3 mqtt_wireless_log.py --host 192.168.1.100`

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<table>
  <tr>
    <td align="center"><a href="https://twitter.com/harsilspatel"><img src="https://avatars1.githubusercontent.com/u/25992839?v=4" width="100px;" alt="Harsil Patel"/><br /><sub><b>Harsil Patel</b></sub></a><br /><a href="https://github.com/monash-human-power/data-acquisition-system/commits?author=harsilspatel" title="Code">💻</a></td>
    <td align="center"><a href="https://khlee.me"><img src="https://avatars3.githubusercontent.com/u/18709969?v=4" width="100px;" alt="Angus Lee"/><br /><sub><b>Angus Lee</b></sub></a><br /><a href="https://github.com/monash-human-power/data-acquisition-system/commits?author=khanguslee" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/pdgra1"><img src="https://avatars3.githubusercontent.com/u/33751672?v=4" width="100px;" alt="pdgra1"/><br /><sub><b>pdgra1</b></sub></a><br /><a href="https://github.com/monash-human-power/data-acquisition-system/commits?author=pdgra1" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/hallgchris"><img src="https://avatars2.githubusercontent.com/u/17876556?v=4" width="100px;" alt="Christopher Hall"/><br /><sub><b>Christopher Hall</b></sub></a><br /><a href="https://github.com/monash-human-power/data-acquisition-system/commits?author=hallgchris" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/chamaka1"><img src="https://avatars0.githubusercontent.com/u/35440106?v=4" width="100px;" alt="chamaka wijesinghe"/><br /><sub><b>chamaka wijesinghe</b></sub></a><br /><a href="https://github.com/monash-human-power/data-acquisition-system/commits?author=chamaka1" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/rileyclarke"><img src="https://avatars1.githubusercontent.com/u/24428011?v=4" width="100px;" alt="Riley Clarke"/><br /><sub><b>Riley Clarke</b></sub></a><br /><a href="https://github.com/monash-human-power/data-acquisition-system/commits?author=rileyclarke" title="Code">💻</a></td>
  </tr>
</table>

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
