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
    - [Picking Microphone](#picking-microphone)
    - [Tuning Microphone](#tuning-microphone)
    - [Tuning Sensitivity](#tuning-sensitivity)
- [Running](#running-assistant)

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
2021-05-16T12:32:49Z model.rs:232 - (tensorflow-models): Loading models/100k-eu-nt/
2021-05-16 13:32:49.864580: I tensorflow/cc/saved_model/reader.cc:31] Reading SavedModel from: models/100k-eu-nt/
2021-05-16 13:32:49.886595: I tensorflow/cc/saved_model/reader.cc:54] Reading meta graph with tags { serve }
2021-05-16 13:32:49.956179: I tensorflow/cc/saved_model/loader.cc:182] Restoring SavedModel bundle.
2021-05-16 13:32:50.226253: I tensorflow/cc/saved_model/loader.cc:132] Running initialization op on SavedModel bundle.
2021-05-16 13:32:50.275430: I tensorflow/cc/saved_model/loader.cc:285] SavedModel load for tags { serve }; Status: success. Took 412419 microseconds.
2021-05-16T12:32:50Z model.rs:281 - (tensorflow-models): Successfully loaded session from saved model
2021-05-16T12:32:50Z model.rs:84 - Loading tensor audio
2021-05-16T12:32:50Z model.rs:118 - Successfully loaded tensor "audio"
2021-05-16T12:32:50Z model.rs:84 - Loading tensor embeddings
2021-05-16T12:32:50Z model.rs:118 - Successfully loaded tensor "embeddings"
2021-05-16T12:32:50Z model.rs:84 - Loading tensor project
2021-05-16T12:32:50Z model.rs:118 - Successfully loaded tensor "project"
2021-05-16T12:32:50Z model.rs:84 - Loading tensor distances
2021-05-16T12:32:50Z model.rs:118 - Successfully loaded tensor "distances"
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dsnoop.c:575:(snd_pcm_dsnoop_open) The dsnoop plugin supports only capture stream
ALSA lib pcm_dsnoop.c:638:(snd_pcm_dsnoop_open) unable to open slave
ALSA lib pcm_dmix.c:1108:(snd_pcm_dmix_open) unable to open slave
ALSA lib pcm_dmix.c:1108:(snd_pcm_dmix_open) unable to open slave
ALSA lib pcm_dmix.c:1108:(snd_pcm_dmix_open) unable to open slave
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dsnoop.c:575:(snd_pcm_dsnoop_open) The dsnoop plugin supports only capture stream
thread 'main' panicked at 'Failed to start audio recording:

--- Friday Error ---


0   friday-audio/src/friday_cpal.rs:106:17 Could not setup any recording device...
1   friday-audio/src/friday_cpal.rs:85:25 Could not find any device matching default


--- End ---
', src/main.rs:37:10
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace

```

This is expected since we have not plugged in the microphone yet. If you got some other type of error, please open an issue. 

In the final section we will be configuring the assistant for your microphone.



### Configuring

This section describes how to pick your microphone, how to tune the microphone, how to tune the sensitivity and how to create a service.

#### Picking Microphone

Plug in your microphone in the pi, then on the raspberry pi run


```bash
arecord -L
```

This will show all of your audio devices, on my raspberry pi it shows

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
front:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    Front speakers
surround21:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    2.1 Surround output to Front and Subwoofer speakers
surround40:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    4.0 Surround output to Front and Rear speakers
surround41:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    4.1 Surround output to Front, Rear and Subwoofer speakers
surround50:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    5.0 Surround output to Front, Center and Rear speakers
surround51:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    5.1 Surround output to Front, Center, Rear and Subwoofer speakers
surround71:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    7.1 Surround output to Front, Center, Side, Rear and Woofer speakers
iec958:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    IEC958 (S/PDIF) Digital Audio Output
dmix:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    Direct sample mixing device
dsnoop:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    Direct sample snooping device
hw:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    Direct hardware device without any conversions
plughw:CARD=MICCU100BK,DEV=0
    nedis  MICCU100BK, USB Audio
    Hardware device with all software conversions

```

I see that the default device is the nedis microphone I bought for the assistant, to pick what device the assistant should use I copy the device ID into 'recording.json', like so:

```bash
{
  "loudness": 1,
  "device": "default:CARD=MICCU100BK"
}
```

> This is the content of recording.json




#### Tuning Microphone

Once we have picked the microphone, try starting the assistant again


```bash
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
```

This time around the assistant should start, the logging should look something like so:


```bash
pi@raspberrypi:~/release-raspberrypi3$ FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
2021-05-16T12:43:17Z model.rs:232 - (tensorflow-models): Loading models/100k-eu-nt/
2021-05-16 13:43:17.329090: I tensorflow/cc/saved_model/reader.cc:31] Reading SavedModel from: models/100k-eu-nt/
2021-05-16 13:43:17.339458: I tensorflow/cc/saved_model/reader.cc:54] Reading meta graph with tags { serve }
2021-05-16 13:43:17.382299: I tensorflow/cc/saved_model/loader.cc:182] Restoring SavedModel bundle.
2021-05-16 13:43:17.517050: I tensorflow/cc/saved_model/loader.cc:132] Running initialization op on SavedModel bundle.
2021-05-16 13:43:17.555874: I tensorflow/cc/saved_model/loader.cc:285] SavedModel load for tags { serve }; Status: success. Took 226754 microseconds.
2021-05-16T12:43:17Z model.rs:281 - (tensorflow-models): Successfully loaded session from saved model
2021-05-16T12:43:17Z model.rs:84 - Loading tensor audio
2021-05-16T12:43:17Z model.rs:118 - Successfully loaded tensor "audio"
2021-05-16T12:43:17Z model.rs:84 - Loading tensor embeddings
2021-05-16T12:43:17Z model.rs:118 - Successfully loaded tensor "embeddings"
2021-05-16T12:43:17Z model.rs:84 - Loading tensor project
2021-05-16T12:43:17Z model.rs:118 - Successfully loaded tensor "project"
2021-05-16T12:43:17Z model.rs:84 - Loading tensor distances
2021-05-16T12:43:17Z model.rs:118 - Successfully loaded tensor "distances"
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dmix.c:1043:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dsnoop.c:575:(snd_pcm_dsnoop_open) The dsnoop plugin supports only capture stream
ALSA lib pcm_dsnoop.c:638:(snd_pcm_dsnoop_open) unable to open slave
ALSA lib pcm_dmix.c:1108:(snd_pcm_dmix_open) unable to open slave
2021-05-16T12:43:17Z friday_cpal.rs:82 - Found recording device default:CARD=MICCU100BK
2021-05-16T12:43:17Z friday_cpal.rs:109 - Using device default:CARD=MICCU100BK
2021-05-16T12:43:17Z server.rs:113 - Starting Server on 0.0.0.0:8000
2021-05-16T12:43:17Z karta_site.rs:46 - new
2021-05-16T12:43:17Z serving.rs:58 - Purging some audio... (takes 2 seconds)
2021-05-16T12:43:19Z serving.rs:66 - Listening..
2021-05-16T12:43:19Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 288, peaks > 6000: 0
2021-05-16T12:43:20Z vad_peaks.rs:43 - Max peak 2006, peaks > 6000: 0
2021-05-16T12:43:21Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:21Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:21Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:21Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:22Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:22Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:22Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:22Z karta_site.rs:133 - Discovery: https://discoverfriday.se/ping status 200
2021-05-16T12:43:22Z discovery.rs:86 - Discovery - Waiting for 3595 seconds
2021-05-16T12:43:22Z vad_peaks.rs:43 - Max peak 2366, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 1853, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 881, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 3777, peaks > 6000: 0
2021-05-16T12:43:23Z vad_peaks.rs:43 - Max peak 3777, peaks > 6000: 0
2021-05-16T12:43:24Z vad_peaks.rs:43 - Max peak 3777, peaks > 6000: 0

```

We need to tune the VAD detection, currently the inference will not start unless the audio peaks above 6000, when I spoke the audio went as high as 3777 which is still too low. This is because my microphone is too quiet.


To fix this I turn up the volume of my microphone using the command 'alsamixer', feel free to use your favorite volume control though.  Now with a louder microphone I 
trigger the inference when I am talking.

```bash
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
```

You can tune the VAD barrier yourself if you want in vad_peaks.json, but I recommend using 6000, or higher, if you can make it work with your microphone. Once the VAD is tuned you can remove its logging, by setting verbose to false in vad_peaks.json



#### Tuning Sensitivity

Start the assistant again


```bash
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf
```

Then open the GUI by either

1. Open discoverfriday.se and pick your device name
2. Navigate to the Pi's local IP at port 8000

You can use the GUI to record a few examples, **TODO** include link here to DEMO to show how.

For example, I recorded one example for 4 different keywords in the GUI

- släck ljuset (Swedish for torn off the light)
- tänd ljuset (Swedish for turn on the light)
- cookies
- movie time

Then I tried saying the words, and also just talked randomly afterwards.

```bash
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

Using this you can see the 'distance' your speech is from the keywords as you speak, you can use this logging information to tune the sensitivity of the model, see ddl.json. I myself picked 0.4, if you want it to be more trigger happy then a higher number is good. If you want it to be more conservative a lower number is good.

A trick is to have multiple recordings per keyword and then quite a low sensitivity, this will make it very conservative and reduce the number of false positivies.



## Running Assistant

Once you have a configured assistant deployed on your pi you could technically just start it with

```bash                                                                                                                                                                                    
FRIDAY_GUI=becky FRIDAY_CONFIG=. ./friday-armv7-unknown-linux-gnueabinhf 
```

and leave it, but if you're SSHing into the assistant it means that the assistant will die as soon as the SSH session dies. A quick workaround for this is to launch it in tmux or screen, I myself like to make use of tmux. But this has the drawback that you have to restart the assistant manually everytime the raspberry pi is restarted.

Instead you can install the assistant service on the pi with

```bash                                                                                                                                                                                    
./install.sh --install
```

Then enable auto restart with

```bash                                                                                                                                                                                    
./install.sh --enable
```


And start Assistant


```bash                                                                                                                                                                                    
./install.sh --start
```

To watch stdout when assistant is started as a service, use:

```bash                                                                                                                                                                                    
sudo journalctl -u friday.service
```







