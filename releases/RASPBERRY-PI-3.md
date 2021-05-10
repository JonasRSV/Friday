# Raspberry Pi 3 

This here is a installation and configuration guide for setting up the Friday assistant on a Raspberry Pi. The guide was developed on a linux laptop but it should translate pretty well to mac too. 

- [Prerequisites](#prerequisites)
- [Setting up the Raspberry Pi](#setting-up-the-raspberry-pi)
- [Installing Assistant](#installation)
  - [Releases](#releases)
    - [Prebuilt](#prebuilt)
    - [Build](#build)
  - [Deploying](#deploying)
  - [Configuring](#configuring)

## Prerequisites

![hardware](../art/raspberry-pi-guide-hardware.png)


- Raspberry pi
- Charger
- SD-card 
- SD-card adapter
- Microphone
- Laptop to Flash SD-card and build release


## Setting up the Raspberry Pi

For this guide I used the Raspberry Pi OS Lite, it can be found on the Raspberry Pi [OS page](https://www.raspberrypi.org/software/operating-systems/). Start by following [this guide](https://www.raspberrypi.org/documentation/installation/installing-images/) to install the operating system onto your SD card.


Secondly, we want to start the SSH server and connect the raspberry pi to your wifi. Begin by inserting the flashed SD card then plug in the Raspberry Pis power and connect it to a screen with keyboard and mouse. If all went well you should see the login screen, since it is your first login the username and password is


```bash
username = pi
password = raspberry
```

Once logged in change the default password using 

```bash
sudo passwd pi
```

For future reference in this guide the environment variables 

```bash
PIUSER=pi
PIPASS=..
```

will be used to reference your pis username and password. Now on your pi in the terminal type


```bash
sudo raspi-config
```

Navigate into interface options and enable SSH. Then go into, in raspi-config, System Options and pick 'Wireless LAN' to join the wifi, the SSID is the name of your wifi. Once you're done with raspi-config it should give you the option to reboot, do so.


Once logged in again you should be able to see your devices local ip using 

```bash
ifconfig
```

Use

```bash
ifconfig | grep inet
```

to see only the rows with ipv4 addresses. For future reference in the guide the PIs ip will be refered to as

```bash
PIIP=..
```

In my case it is

```bash
PIIP=192.168.1.19
```

You should now be able to unplug the keyboard, mouse and screen from the raspberry pi and connect to it via ssh. To check that all up until this point is working try connecting to the pi via SSH

```bash
ssh ${PIUSER?}@${PIIP?}
```


Using SSH is not necessary but it is convenient, we will use it to move files between your computer and the Pi when installing the assistant. Technically this can be done without SSH by moving files using a USB or other means, if you don't like SSH just substitute all file transfers with your favorite method.






## Installation

The installation of the assistant is done in three steps

1. [Aquire a Release](#releases)
2. [Deploy](#deploying) Release on Assistant
3. [Configure](#configuring) Assistant


### Releases

The first step is to aquire a release of the assistant.

#### Prebuilt

Prebuilt releases are not available yet :/, build your own! 

#### Build

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


### Configuring
