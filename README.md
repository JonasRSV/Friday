![logo](art/friday-logo.png)

Friday is a keyword spotting based voice assistant. The main feature is that it is wake word free, offline and uses few-shot learning to add new keywords. 

- [Installation](#installation)
- [Releases](#releases)
- [Contributing](#contributing)
- [Architecture](#architecture)



TODO.. Demo


## Installation

Installation has been tested on the following platforms, using rusts cross-compilation tools

- [Raspberry Pi 3](releases/INSTALL-RASPBERRY-PI-3.md)
- [Linux x86](releases/INSTALL-LINUX-x86.md)


## Releases

TODO..


## Contributing

Any and all contributions are welcome - preferably through a PR. 

## Architecture


The Friday project consists of three components

1. [friday binary](#friday-binary), found in [friday](friday)
2. [model development](#models), found in [mm](mm)
3. [guis & web](#gui-&-web), found in [web](web)

### Friday Binary

The main binary found under [/friday](friday) contains the following modules

![diagram](art/friday-binary.png)

audio is recorded with **friday-audio**, **friday-vad** is a low resource barrier to **friday-inference**. **friday-vad** executes keywords spotted by **friday-inference**. Each module uses the utility modules **friday-error**, **friday-logging** and **friday-storage** for persistance, logging and error handling. Each module also implements endpoint via **friday-web** which is used to get information and set information via an API. This enables adding keywords and configuring the assistant via a WebGUI. **friday-discovery** exposes functionality to make finding the assistant eaiser. **friday-signal** is under development but is ment to be used by the assistant to send physical signals, such as noise or light to indicate to the user at what stage of the inference pipeline the model is at.


### Models 

Models are developed under mm/


### Gui & Web

The latest web gui, that I myself use is [nightout](web/nightout), there is no API documentation at the moment. But [this file](web/nightout/src/FridayAPI.js) contains a majority of the API endpoint to talk to friday.
