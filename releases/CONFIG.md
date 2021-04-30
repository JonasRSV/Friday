# Assistant configs
---

## ddl.json

This file contains configurations for the inference engine.

```javascript
{
  "export_dir": "models/ddl_apr_13_eu",
  "sensitivity": 0.6,
  "frames": 1,
  "audio": {
  }
}
```

**export_dir** is the path to the tensorflow saved model.

**sensitivity** A value of 0 means the model only reacts to perfect matches and a value of infinity means it will react to everything.

**frames** smoothing of the inference, 1 frame means the model will react as soon as a audio frame is below the sensitivity for some keyword. n frames means the average across n frames needs to be below sensitivity.

**audio** a key value map mapping audio file names to the utterance it contains. This does not need to be touched since it is populated by the GUI.


## discovery.json

This file contains configurations for the discovery engine

```javascript

{
  "name": "DEVICE_NAME_HERE"
}
```

**name** is the device name of your assistant, e.g (Albert)

## recording.json

This file contains configuration for the recording module

```javascript
{
  "loudness": 1,
  "device": "default"
}
```

**loudness** is a multiplier for each sample, if your microphone is very quiet this can be used to increase the volume if there are no other means. The inference module works best if the 'Max-Peak' (see later configs) is above 5k when you're saying the keyword.

**device** The microphone you want the assistant to use for recording. You can use 
```bash
arecord -L
```

to list available devices

## scripts.json

for example:

```javascript
{
  "scripts": {
    "illuminati": [
      "hello_world.py"
    ]
  }
}

```

The following configuration makes it so that when 'illuminati' is uttered friday will execute the script 'scripts/hello_world.py'. This does not need to be populated manually, but rather it can be done in the GUI.


## vad_peaks.json

{
  "min_peaks": 4,
  "min_peak_height": 13000,
  "verbose": true
}

**min_peaks** the minimum number of peaks with 'min_peak_height' that need to be present in the audio to pass

**min_peak_height** the minimum height of peaks in audio that counts towards min_peaks

**verbose** if true, prints the max peak in the audio and number of peaks larger than min_peaks


## discovery/kartasite.json


{
  "site_url": "https://discoverfriday.se/ping"
}


**site_url** url to site it will ping with information to make it possible to find your Friday on https://discoverfriday.se/ (your device name will show up on that page and it will link to your Fridays local IP.


