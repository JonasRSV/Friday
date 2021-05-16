# Raspberry Pi 3 

This is the installation and configuration guide for setting up Friday on a Raspberry Pi. The guide was developed on a Linux laptop.

- [Prerequisites](#prerequisites)
- [Setting up the Raspberry Pi](#setting-up-the-raspberry-pi)
- [Installing Assistant](#installation)
  - [Releases](#releases)
    - [Prebuilt](#prebuilt)
    - [Build](#build)
  - [Deploying](#deploying)
    - [Installing libtensorflow](#installing-libtensorflow)
    - [Installing release](#installing-release)
  - [Configuring](#configuring)
    - [Picking Microphone](#picking-microphone)
    - [Tuning Microphone](#tuning-microphone)
    - [Tuning Sensitivity](#tuning-sensitivity)
- [Running Assistant](#running-assistant)

## Prerequisites

![hardware](../art/raspberry-pi-guide-hardware.png)


- Raspberry pi
- Charger
- SD-card 
- SD-card adapter
- Microphone



## Setting up the Raspberry Pi

For the Operating System I recommend using Raspberry Pi OS Lite, it can be found on the Raspberry Pi [OS page](https://www.raspberrypi.org/software/operating-systems/). Follow the [Raspberry Pi OS install guide](https://www.raspberrypi.org/documentation/installation/installing-images/) to flash the operating system onto your SD card. Thereafter enable WIFI and SSH on your Pi, do this by plugging in a keyboard, mouse and monitor into the raspberry pi and then start it. If this is your first time starting it you can log in with the default credentials

```bash
username = pi
password = raspberry
```

It is then recommended to change the default password for your raspberry Pi, do this with ```sudo passwd pi```. For future reference ```PIUSER=pi``` and ```PIPASS=..``` will represent your user and password in this guide.  Now when logged into your Pi enable SSH and WIFI, an easy way to do this is by typing ```sudo raspi-config``` into the terminal. Then under **Interface Options** you will be able to start the SSH server and under **System Options** you can log into the WIFI.  Once you're done with raspi-config it should give you the option to reboot, do so.


Once restarted use ```ifconfig | grep inet``` to get the IP address. For example my Pi has 

```bash
inet 127.0.0.1  netmask 255.0.0.0
inet6 ::1  prefixlen 128  scopeid 0x10<host>
inet 192.168.1.19  netmask 255.255.255.0  broadcast 192.168.1.255
inet6 fe80::4f2d:1ce2:ead1:961f  prefixlen 64  scopeid 0x20<link>
```

and 192.168.1.19 is the address I am looking for. Remember the IP adress, now you can unplug the Keyboard, Mouse and Screen and connect to the Raspberry Pi using SSH. For future reference ```PIIP=192.168.1.19``` will be used to refer to the Pis IP in this guide, exchange my IP adress for yours. It should now be possible to connect to the Pi, with for example: 

```bash
ssh ${PIUSER?}@${PIIP?}
```


## Installation

The installation of the assistant is done in three steps. First we aquire a release, then we deploy this release onto the Raspberry Pi and finally we can configure it. Unfortunately some manual configuration has to be done to make it work well with different microphones.

1. [Aquire a Release](#releases)
2. [Deploy](#deploying) Release on Assistant
3. [Configure](#configuring) Assistant


### Releases

Begin by aquiring an assistant release, either a prebuilt one or if you want the lastest features build it yourself from the main branch.

#### Prebuilt

Go to the [release page](https://github.com/JonasRSV/Friday/releases/tag/v0.01) and download latest 'pi-release.zip'

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

Before deploying the assistant release on the Raspberry Pi we must make sure that libtensorflow is installed on the Pi, and if not: install it. [libtensorflow](https://www.tensorflow.org/install/lang_c) is used for serving of the deep learning models and has to be installed on the system.

- [Installing libtensorflow](#installing-libtensorflow)
- [Installing release](#installing-release)

You can check for a libtensorflow installation using

```bash
ldconfig -p | grep tensorflow
```

If the output is empty, it is not installed.


#### Installing libtensorflow

libtensorflow is provided under [platforms.Resources](../platforms.Resources). Download the zip file for Raspberry Pi and copy it to the Raspberry Pi, then install it into your Pis library. One way of doing this is provided with the following sequence of commands.

First copy the library from your computer onto the Raspberry Pi

```bash
scp platforms.Resources/libtensorflow-unknown-linux-pi32.zip ${PIUSER?}@${PIIP?}:/home/${PIUSER?}
```

Then connect to your Pi

```bash
ssh ${PIUSER?}@${PIIP?}
```

Open the library file on your Pi

```bash
unzip libtensorflow-unknown-linux-pi32.zip
```

Move the files to the system library and update the cache

```bash
sudo mv *.so /usr/lib && sudo ldconfig
```

You can now verify the installation again, if you see something similar to

```bash
pi@raspberrypi:~$ ldconfig -p | grep tensorflow
        libtensorflow_framework.so (libc6,hard-float) => /lib/libtensorflow_framework.so
        libtensorflow.so (libc6,hard-float) => /lib/libtensorflow.so

```

all likely went well.


#### Installing release


Assuming you got your hands on a ```pi-release.zip``` from the [releases step](#releases). Move it to and unzip it on the Raspberry Pi, one way of doing this is exemplified with the following commands.

```bash
scp pi-release.zip ${PIUSER?}@${PIIP?}:/home/${PIUSER?}
```

Then connect to your Pi

```bash
ssh ${PIUSER?}@${PIIP?}
```

Open with

```bash
unzip pi-release.zip
```

You should now see

```bash
pi@raspberrypi:~$ ls
empty  pi-release.zip  release-raspberrypi3
```

The important folder is the ```release-raspberrypi3``` folder. Navigate into it and try starting the assistant


```bash
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
```

If you haven't plugged in your microphone yet you should see something like:

```bash
.
.
.

--- Friday Error ---


0   friday-audio/src/friday_cpal.rs:106:17 Could not setup any recording device...
1   friday-audio/src/friday_cpal.rs:85:25 Could not find any device matching default


--- End ---

.
.
.

```

Where the dots represent additional logging. This is completely expected, in the next section we will plug in the microphone and configure the assistant.


### Configuring

In this section we will pick our microphone, tune microphone configurations and tune model sensitivity.

- [Picking Microphone](#picking-microphone)
- [Tuning Microphone](#tuning-microphone)
- [Tuning Sensitivity](#tuning-sensitivity)

All configuration options are described in [CONFIG.md](CONFIG.md), in this guide we only cover the most essential ones.


#### Picking Microphone

Plug in your favorite Microphone in the Raspberry Pi and connect to the Raspberry Pi ```ssh ${PIUSER?}@${PIIP?}```. On your Pi you can list all the connected audio devices with ```arecord -L```, on my Pi it gives the following output

```bash
pi@raspberrypi:~/release-raspberrypi3$ arecord -L
null
    Discard all samples (playback) or generate zero samples (capture)
default:CARD=MICCU100BK
    nedis  MICCU100BK, USB Audio
    Default Audio Device
sysdefault:CARD=MICCU100BK
    nedis  MICCU100BK, USB Audio
    Default Audio Device
.
.
.
```

Copy the ID of the audio device you want to use into the ```recording.json``` configuration. For example my configuration uses the default nedis microphone

```bash
{
  "loudness": 1,
  "device": "default:CARD=MICCU100BK"
}
```

> This is the content of recording.json


Now we are ready to start tuning the assistant for this microphone.



#### Tuning Microphone

Try starting the assistant again


```bash
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
```

Once its on, look at the logging and start making some noise, you should be able to observe logging lines such as 


```bash
.
.
.

2021-05-16T12:43:19Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 2006, peaks > 6000: 0
2021-05-16T12:43:21Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:22Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 1853, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 881, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 3777, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 3777, peaks > 6000: 0
2021-05-16T12:43:24Z vad_peaks.rs:43 - Max peak 3777, peaks > 6000: 0

.
.
.
```

Begin by setting the volume on the microphone such that Max peak is above 6000 when you're uttering your keywords. Preferably significantly above 6000, I would say around 10 000 is good. You can use ```alsamixer``` and also the loudness configuration in ```recording.json``` to tune the volume, or your favorite volume control tool. It is also possible to tune the Voice Activity Detection (VAD) in the ```vad_peaks.json```. I don't recommend lowering the peak threshold, if anything you can increse it.

Once my volume was tuned the logging looked like so


```bash
.
.
.

2021-05-16T12:46:48Z vad_peaks.rs:43 - Max peak 8388, peaks > 6000: 128
2021-05-16T12:46:48Z interface.rs:370 - Cannot infer without examples
2021-05-16T12:46:48Z vad_peaks.rs:43 - Max peak 8388, peaks > 6000: 128
2021-05-16T12:46:48Z interface.rs:370 - Cannot infer without examples
2021-05-16T12:46:48Z vad_peaks.rs:43 - Max peak 8388, peaks > 6000: 128
2021-05-16T12:46:48Z interface.rs:370 - Cannot infer without examples
2021-05-16T12:46:48Z karta_site.rs:133 - Discovery: https://discoverfriday.se/ping status 200
2021-05-16T12:46:48Z discovery.rs:86 - Discovery - Waiting for 3595 seconds
2021-05-16T12:46:48Z vad_peaks.rs:43 - Max peak 7370, peaks > 6000: 30
2021-05-16T12:46:48Z interface.rs:370 - Cannot infer without examples
2021-05-16T12:46:49Z vad_peaks.rs:43 - Max peak 3826, peaks > 6000: 0
2021-05-16T12:46:49Z serving.rs:140 - Model was reset
2021-05-16T12:46:49Z vad_peaks.rs:43 - Max peak 9080, peaks > 6000: 27

.
.
.
```


With the microphone tuned we are ready to [run the assistant](#running-assistant) or optionally, and recommended, [tune the sensitivity](#tuning-sensitivity) of the assistant for your use case. Once it is tuned, I recommend turning of the verbose VAD logging, do this by setting ```verbose: false``` in ```vad_peaks.json```.


#### Tuning Sensitivity

Assuming that the assistants microphone is properly configured: configure the sensitivity by adding a few example keywords and observe the inference logging as you're speaking. Use the inference logging to decide on a value for ```sensitivity``` in ```ddl.json```. One way of doing this is exemplified here

Begin by starting the assistant on the Raspberry Pi

```bash
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
```

Then open its GUI by one of the following methods

1. Open discoverfriday.se and pick your device name (If [discovery/karta_site.json](platform.common/discovery/kartasite.json) is enabled)
2. Navigate to the Pi's local IP at port 8000

Use the GUI to add a few keywords. Look at the demo for an example of how that is done


For example, I recorded one example for four different keywords.

- släck ljuset (Swedish for torn off the light)
- tänd ljuset (Swedish for turn on the light)
- cookies
- movie time

Then I tried saying the words, and also just talked randomly afterwards.

```bash
.
.
.

2021-05-16T13:00:43Z interface.rs:391 - D(movie time ) = 0.84672344 -- M(movie time ) = 0.84672344
2021-05-16T13:00:44Z interface.rs:391 - D(släck ljuset) = 0.41937762 -- M(släck ljuset) = 0.41937762
2021-05-16T13:00:44Z interface.rs:391 - D(släck ljuset) = 0.34784487 -- M(släck ljuset) = 0.34784487
2021-05-16T13:00:44Z serving.rs:100 - Dispatching släck ljuset
2021-05-16T13:00:46Z serving.rs:140 - Model was reset
2021-05-16T13:00:48Z interface.rs:391 - D(cookies) = 0.9224455 -- M(cookies) = 0.9224455
2021-05-16T13:00:48Z interface.rs:391 - D(tänd ljuset) = 0.4031582 -- M(tänd ljuset) = 0.4031582
2021-05-16T13:00:48Z interface.rs:391 - D(tänd ljuset) = 0.39649865 -- M(tänd ljuset) = 0.39649865
2021-05-16T13:00:48Z serving.rs:100 - Dispatching tänd ljuset
2021-05-16T13:00:51Z serving.rs:140 - Model was reset
2021-05-16T13:00:51Z interface.rs:391 - D(cookies) = 0.7698038 -- M(cookies) = 0.7698038
2021-05-16T13:00:52Z interface.rs:391 - D(cookies) = 0.17028648 -- M(cookies) = 0.17028648
2021-05-16T13:00:52Z serving.rs:100 - Dispatching cookies
2021-05-16T13:00:54Z serving.rs:140 - Model was reset
2021-05-16T13:00:55Z interface.rs:391 - D(movie time ) = 0.6395974 -- M(movie time ) = 0.6395974
2021-05-16T13:00:56Z interface.rs:391 - D(movie time ) = 0.21833037 -- M(movie time ) = 0.21833037
2021-05-16T13:00:56Z serving.rs:100 - Dispatching movie time 
2021-05-16T13:00:58Z serving.rs:140 - Model was reset
2021-05-16T13:01:00Z interface.rs:391 - D(cookies) = 0.91462433 -- M(cookies) = 0.91462433
2021-05-16T13:01:00Z interface.rs:391 - D(movie time ) = 0.81361586 -- M(movie time ) = 0.81361586
2021-05-16T13:01:01Z interface.rs:391 - D(movie time ) = 0.7030568 -- M(movie time ) = 0.7030568
2021-05-16T13:01:01Z interface.rs:391 - D(movie time ) = 0.8395334 -- M(movie time ) = 0.8395334
2021-05-16T13:01:02Z interface.rs:391 - D(movie time ) = 0.6405574 -- M(movie time ) = 0.6405574
2021-05-16T13:01:02Z interface.rs:391 - D(movie time ) = 0.6094059 -- M(movie time ) = 0.6094059
2021-05-16T13:01:02Z interface.rs:391 - D(movie time ) = 0.6063254 -- M(movie time ) = 0.6063254
2021-05-16T13:01:03Z interface.rs:391 - D(movie time ) = 0.6486774 -- M(movie time ) = 0.6486774
2021-05-16T13:01:03Z interface.rs:391 - D(movie time ) = 0.6916123 -- M(movie time ) = 0.6916123
2021-05-16T13:01:03Z serving.rs:140 - Model was reset
2021-05-16T13:01:07Z interface.rs:391 - D(movie time ) = 0.87294084 -- M(movie time ) = 0.87294084
2021-05-16T13:01:07Z interface.rs:391 - D(movie time ) = 0.82693267 -- M(movie time ) = 0.82693267
2021-05-16T13:01:07Z interface.rs:391 - D(movie time ) = 0.8408278 -- M(movie time ) = 0.8408278
2021-05-16T13:01:08Z interface.rs:391 - D(movie time ) = 0.7395995 -- M(movie time ) = 0.7395995
2021-05-16T13:01:08Z interface.rs:391 - D(movie time ) = 0.64777195 -- M(movie time ) = 0.64777195
2021-05-16T13:01:09Z interface.rs:391 - D(movie time ) = 0.6956604 -- M(movie time ) = 0.6956604

```

Using this I settled on a sensitivity of 0.4. A high value will make the assistant more trigger happy and a low value less so.  One trick is to have a lower value and then provide multiple example recordings per keyword. 



## Running Assistant

With a configured and tuned assistant you could just start it ```FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf ``` and leave it. But if you for example SSH'd to connect to the Pi this means the assistant is only alive as long as the SSH session, to mitigate this you can use tmux or screen. But even if you persist the assistant across SSH sessions it would have to be manually restarted everytime the Raspberry Pi is restarted. 

For convenience the Raspberry Pi release contains a service file which can be used to turn the assistant into a system service so that it is automatically started when the Raspberry Pi is started. You can install this system service with the following sequence of commands on the Raspberry Pi.


Copy the friday.service file with:

```bash                                                                                                                                                                                    
./install.sh --install
```

Enable the Service with (makes sure it will start on boot)

```bash                                                                                                                                                                                    
./install.sh --enable
```

Start assistant for current boot with


```bash                                                                                                                                                                                    
./install.sh --start
```

Check assistant status with

```bash                                                                                                                                                                                    
./install.sh --status
```

To watch stdout when assistant is started as a service, use:

```bash                                                                                                                                                                                    
sudo journalctl -u friday.service
```







