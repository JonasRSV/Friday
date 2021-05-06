# Raspberry Pi 3 

- [Prerequisites](#prerequisites)
- [Setting up Raspberry Pi](#raspberry-pi)
- [Installing Assistant](#installation)
  - [Releases](#releases)
  - [Build](#build)
  - [Deploying](#deploying)

## Prerequisites

![hardware](../art/raspberry-pi-guide-hardware.png)


You need

- Raspberry pi
- Charger
- SD-card 
- SD-card adapter
- Microphone
- Laptop to Flash SD-card and build release


## Raspberry Pi

TODO flash SD card etc..


## Installation

In order to install the assistant you need to build or use an existing release

### Releases

Releases are not available yet, build your own! 

### Build

Start with cloning this repository 

```bash
git clone https://github.com/JonasRSV/Friday
```

Navigate into the root

```bash
cd Friday
```


Use the build script to build the Friday binary, the script will use [cross](https://github.com/rust-embedded/cross) to cross compile in a docker container.


```bash
./build -pi
```

It is likely that you are missing a lot of dependencies, the build script will give you instructions on what is missing and where to install it from. Once the binary is built you should see it in

```bash
ls $PWD/bin
```

To create a release: a bundle with files for GUI, model, configurations and the binary; run the release script

```bash
./release -pi
```

This should create a directory under releases/release-raspberrypi3 that contains all files necessary to launch the assistant. Put them all in a zip file

```bash
zip -r pi-release.zip releases/release-raspberrypi3
```

### Deploying 

TODO.. copy release to assistant, make sure libtensorflow is installed and voila run it!
