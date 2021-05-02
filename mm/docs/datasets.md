# Datasets
---

## Google Speech Commands

This dataset is used for evaluation

```bash
FRIDAY_DATA=data
mkdir -p $FRIDAY_DATA/google_speech_commands
cd $FRIDAY_DATA/google_speech_commands \
    && curl -L http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz > speech_commands.tar.gz \
    && tar -xvf speech_commands.tar.gz
```

## Mozilla Common Voice

This dataset is used for training. Go through their instructions on the website to download.

[common voice](https://commonvoice.mozilla.org/sv-SE/datasets) is a open-source dataset provided by mozilla. 

## LibriSpeech


[LibriSpeech](http://www.openslr.org/12) is a open ASR dataset, it is used for training.

Run the following script to download the data
```bash
FRIDAY_DATA=data ./scripts/download_librispeech.sh
```
