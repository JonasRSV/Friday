# Raspberry Pi 3 

This here is a installation and configuration guide for setting up the Friday assistant on a Raspberry Pi. The guide was developed on a linux laptop but it should translate pretty well to mac too. 

- [Prerequisites](#prerequisites)
- [Setting up the Raspberry Pi](#setting-up-the-raspberry-pi)
- [Installing Assistant](#installation)
  - [Releases](#releases)
    - [Prebuilt](#prebuilt)
    - [Build](#build)
  - [Deploying](#deploying)
    - [Installing libtensorflow](#installing-libtensorflow)
    - [Installing Assistant on Pi](#installing-assistant-on-pi)
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

to see only the rows with ip addresses. For future reference in the guide the PIs ip will be refered to as

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

The second step is deploying the release on the raspberry pi.  The first time you do this you also have to install libtensorflow on your raspberry pi, it is used by the assistant to serve its deep learning models. 

#### Installing libtensorflow

libtensorflow is provided under friday/platforms.Resources/libtensorflow-unknown-linux-pi32.zip copy it to your pi using

```bash
scp platforms.Resources/libtensorflow-unknown-linux-pi32.zip ${PIUSER?}@${PIIP?}:/home/${PIUSER?}
```

connect to your pi


```bash
ssh ${PIUSER?}@${PIIP?}
```

under /home/pi you should see libtensorflow-unknown-linux-pi32.zip, open it with

```bash
unzip libtensorflow-unknown-linux-pi32.zip
```

Move the files to the system library and update the cache

```bash
sudo mv *.so /usr/lib && sudo ldconfig
```

You should see them when running the following command

```bash
ldconfig -p | grep tensorflow
```

If so, the installation of libtensorflow went well.


#### Installing Assistant on Pi

Assuming you got your hands on a release from the first step, move it to the assistant.

```bash
scp pi-release.zip ${PIUSER?}@${PIIP?}:/home/${PIUSER?}
```

then connect to the pi and open it with 


```bash
unzip pi-release.zip
```

you should now have 'release-raspberrypi3' in '/home/pi'


With this you should be able to start the assistant. Go into the release-raspberrypi3 folder and run

```bash
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
```

However it will quit, with the following message:

```bash
pi@raspberrypi:~/release-raspberrypi3$ FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
2021-05-10T16:15:37Z model.rs:232 - (tensorflow-models): Loading models/ddl_apr_13_eu
2021-05-10 17:15:37.836410: I tensorflow/cc/saved_model/reader.cc:31] Reading SavedModel from: models/ddl_apr_13_eu
2021-05-10 17:15:37.847020: I tensorflow/cc/saved_model/reader.cc:54] Reading meta graph with tags { serve }
2021-05-10 17:15:37.892163: I tensorflow/cc/saved_model/loader.cc:182] Restoring SavedModel bundle.
2021-05-10 17:15:38.031820: I tensorflow/cc/saved_model/loader.cc:132] Running initialization op on SavedModel bundle.
2021-05-10 17:15:38.072427: I tensorflow/cc/saved_model/loader.cc:285] SavedModel load for tags { serve }; Status: success. Took 235980 microseconds.
2021-05-10T16:15:38Z model.rs:281 - (tensorflow-models): Successfully loaded session from saved model
2021-05-10T16:15:38Z model.rs:84 - Loading tensor audio
2021-05-10T16:15:38Z model.rs:118 - Successfully loaded tensor "audio"
2021-05-10T16:15:38Z model.rs:84 - Loading tensor embeddings
2021-05-10T16:15:38Z model.rs:118 - Successfully loaded tensor "embeddings"
2021-05-10T16:15:38Z model.rs:84 - Loading tensor project
2021-05-10T16:15:38Z model.rs:118 - Successfully loaded tensor "project"
2021-05-10T16:15:38Z model.rs:84 - Loading tensor distances
2021-05-10T16:15:38Z model.rs:118 - Successfully loaded tensor "distances"
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dsnoop.c:575:(snd_pcm_dsnoop_open) The dsnoop plugin supports only capture stream
ALSA lib pcm_dsnoop.c:638:(snd_pcm_dsnoop_open) unable to open slave
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dsnoop.c:575:(snd_pcm_dsnoop_open) The dsnoop plugin supports only capture stream
ALSA lib pcm_dsnoop.c:638:(snd_pcm_dsnoop_open) unable to open slave
thread 'main' panicked at 'Failed to start audio recording:

--- Friday Error ---


0   friday-audio/src/friday_cpal.rs:108:17 Could not setup any recording device...
1   friday-audio/src/friday_cpal.rs:86:25 Could not find any device matching default


--- End ---
', src/main.rs:38:10
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

```

This is expected since we have not plugged in the microphone yet. If you got some other type of error, please open an issue. In the final section we will be configuring the assistant, this involves plugging in the microphone and selecting configurations to make it work as well as possible in your environment.






### Configuring
