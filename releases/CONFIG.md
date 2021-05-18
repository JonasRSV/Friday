# Assistant configs
---

This documents presents all the configuration files used by the assistant and what the fields mean.

- [ddl.json](#ddl)
- [discovery.json](#discovery)
  - [kartasite.json](#kartasite)
- [recording.json](#recording)
- [scripts.json](#scripts)
- [vad_peaks.json](#vad_peaks)

### ddl 

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

- **export_dir** is the path to the tensorflow saved model.
- **sensitivity** how sensitive the model is.
  - Value of 0 means to only ever react to perfect matches.
  - Value of infinity mean to always pick the most likely match. 
- **frames** Smoothing of model distances
  - Value of 1 means it reacts as soon as one frame is below sensitivity
  - Value of x means it reacts as soon as the average of x frames is below sensitivity
- **audio** a key value map mapping audio files to keywords.
  - This is typically set by the [user interface](../web/becky) and does not need to be set manually.


## discovery

This file contains configurations for the discovery module

```javascript

{
  "name": "Friday"
}
```

- **name** is the device name of your assistant, e.g (Albert)
  - This name will show up on the GUI and the discovery site
  - It can be used to distinguish multiple assistants on the same network.

### discovery/kartasite


```javascript
{
  "disable": false,
  "site_url": "https://discoverfriday.se/ping"
}
```


- **disable** set to true to disable this functionality.
  - if it is disabled no information will be sent from the assistant to the site url.
  - if disabled https://discoverfriday.se/ won't work for this assistant.
- **site_url** url to site it will ping with discovery information.
  - Navigating to https://discoverfriday.se/ will show all assitant on your local network. 
  - It will send your device name and the assistants local IP to the website.
  - It will update that information once every day if a send is successful 
  - It will retry once every 5 seconds if a send is unsuccessful 



## recording

This file contains configuration for the recording module

```javascript
{
  "loudness": 1,
  "device": "default"
}
```

- **loudness** is a multiplier for volume. 
  - Can be used to increase volume if your mic is very quiet and there is no other way.
  - Should be last resort, try increasing volume through alsamixer or something first.
  - Only supports whole numbers, no decimals.
- **device** The microphone you want the assistant to use for recording. 
  - Use ``arecord -L `` to check for available devices


## scripts

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

- **scripts** is a key value field mapping keywords to a list of scripts.
  - This is typically populated by the [user interface](../web/becky).
  - No need to set this manually.

In the example above when 'illuminati' is uttered friday will execute the script 'scripts/hello_world.py'.


## vad_peaks

```javascript
{
  "min_peaks": 4,
  "min_peak_height": 13000,
  "verbose": true
}
```

- **min_peaks** the minimum number of peaks with 'min_peak_height' that need to be present in the audio to pass to inference
  - 4 is a fine value, typically does not require tuning
- **min_peak_height** the minimum height of peaks in audio that counts towards min_peaks
  - Needs to be tuned on a per mic basis
- **verbose** if true, prints the max peak in the audio and number of peaks larger than min_peaks
  - Set to 'true' to print information that is useful when tuning
  - Set to 'false' when done with tuning to not clutter all other logging.



In general you can control fridays log level with the environment variable

```bash
FRIDAY_LOG_LEVEL=DEBUG
FRIDAY_LOG_LEVEL=INFO
FRIDAY_LOG_LEVEL=WARNING
FRIDAY_LOG_LEVEL=ERROR
FRIDAY_LOG_LEVEL=FATAL
```
