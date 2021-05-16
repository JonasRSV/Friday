# Releases

This folder contains files necessary for deploying to different platforms. This is also where finished releases will end up when running the 'release' script in the root directory.


A brief description of its contents:

- **platform.common** contains files common for all platforms
  - configurations
  - models
- **platform.xx** contains files for platform xx
  - service files
  - startup scripts
- [**CONFIG.md**](CONFIG.md) documentation of the configuration options for Friday.
- [**LINUX-x86.md**](LINUX-x86.md) documentation of how to install on common linux systems
- [**RASPBERRY-PI-3.md**](RASPBERRY-PI-3.md) documentation of how to install on raspberry pi 


Once the release script is run it will produce a folder release-\* which contains the files necessary to deploy the assistant. 

