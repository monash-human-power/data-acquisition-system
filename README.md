# Monash Human Power Data Acquisition System
[![All Contributors](https://img.shields.io/badge/all_contributors-2-orange.svg?style=flat-square)](#contributors)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/632fc262b19f465393f12098555f23ba)](https://app.codacy.com/app/mhp-admin/MHP_DAS?utm_source=github.com&utm_medium=referral&utm_content=Monash-Human-Power/MHP_DAS&utm_campaign=Badge_Grade_Dashboard)

The Data Acquisition System (DAS) allows us to collect and store data from various sensors attached to the bike. The DAS consists of a Raspberry Pi which serves as the main ‘brain’ of the system, and a Teensy LC in which the sensors interface with. This manual acts as an operating guide to use the DAS.

This repository contains all the code related to Monash Human Power's Data Acquisition System (DAS).

# Getting Started
1. Type `git clone https://github.com/Monash-Human-Power/MHP_DAS.git` on the command line to download the whole repository.
2. Type `git submodule update --init` on the command line to download and update the submodules within the repository.

# Contents

## Raspi

### DAS.js
node.js program we run to communicate to the Teensy that is connected to the Raspberry Pi via serial communication.

## Teensy
| Script Name    | Description                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| DAS.ino        | Script that collects data from each sensor                                                                 |
| DAS_MOCK.ino   | Script that mocks fake data coming into the Teensy. Useful for checking if serial communication is working |
| DAS_NO_GPS.ino | DAS.ino with the GPS disabled. Useful for testing the DAS inside.                                          |

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<table>
  <tr>
    <td align="center"><a href="https://twitter.com/harsilspatel"><img src="https://avatars1.githubusercontent.com/u/25992839?v=4" width="100px;" alt="Harsil Patel"/><br /><sub><b>Harsil Patel</b></sub></a><br /><a href="https://github.com/monash-human-power/MHP_DAS/commits?author=harsilspatel" title="Code">💻</a></td>
    <td align="center"><a href="https://khlee.me"><img src="https://avatars3.githubusercontent.com/u/18709969?v=4" width="100px;" alt="Angus Lee"/><br /><sub><b>Angus Lee</b></sub></a><br /><a href="https://github.com/monash-human-power/MHP_DAS/commits?author=khanguslee" title="Code">💻</a></td>
  </tr>
</table>

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!