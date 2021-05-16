
### Architecture


Friday consists of three components

1. [Assistant Binary](#friday-binary), found in [friday](friday)
2. [Model Development](#models), found in [mm](mm)
3. [GUI](web/becky), found in [web](web/becky)

### Friday Binary

The main binary found under [/friday](friday) contains the following modules

![diagram](art/friday-binary.png)

audio is recorded with **friday-audio**, **friday-vad** is a low resource barrier to **friday-inference**. **friday-vendor** executes keywords spotted by **friday-inference**. Each module uses the utility modules **friday-error**, **friday-logging** and **friday-storage** for persistance, logging and error handling. Each module also implements endpoint via **friday-web** which is used to get information and set information via an API. This enables adding keywords and configuring the assistant via a WebGUI. **friday-discovery** exposes functionality to make finding the assistant eaiser. **friday-signal** is under development but is ment to be used by the assistant to send physical signals, such as noise or light to indicate to the user at what stage of the inference pipeline Friday is at.

