# Monash Human Power Data Acquisition System - Middle wireless module

[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors)

The Middle Wireless Module allows us to collect and send data from x sensors attached to the bike. The middle wireless module consists of a micro controller (ESP32 currently) which gathers the data from the on board sensors and sends them using MQTT (using the internet).

This repository contains all the code related to Monash Human Power's middle wireless module - part of their Data Acquisition System (DAS).

## Getting Started

1. Press clone on the root folder and use it to clone the entire repository on the command line.
2. Create a config.py file in the same directory as the contents of this folder (refer below).
3. The config.py file should hold the following variables (ensure the name matches):
- ESSID : Should be assigned to a string containing the SSID of the network to connect to
- PASSWORD: Should be assigned to a string containing password of the network
- MQTT_BROKER: A string containing either the web server name or IP address which acts like the Mqtt broker
- builtin_LED = PIN(2, PIN.OUT)

## Contents
- Boot.py: Contains function to connect the micro controller to the internet



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
