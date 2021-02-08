# Datasets

---

## Common Format 

Datasets, no matter source is currently converted into TFExamples with the following content

```python3
# The audio fields are x seconds recordings of mono 16 bit PCM data 

audio: int64list # Would be nice with int16 list but tfexample does not support it.. which unfortunately makes the dataset 4x larger.
text:  byteslist
sample_rate: int64 # This should pretty much always be 8kHz or 16kHz
label: int64list # This is optional and not always present.
```

This document assumes that your current root is mm

## Google Speech Commands

```bash
FRIDAY_DATA=data
mkdir -p $FRIDAY_DATA/google_speech_commands
cd $FRIDAY_DATA/google_speech_commands \
    && curl -L http://download.tensorflow.org/data/speech_commands_v0.02.tar.gz > speech_commands.tar.gz \
    && tar -xvf speech_commands.tar.gz
```

## FireFox Common Voice Single Word

[common voice](https://commonvoice.mozilla.org/sv-SE/datasets) is a open-source dataset provided by mozilla. 

```bash 
FRIDAY_DATA=data
mkdir -p $FRIDAY_DATA/common_voice_single_word
cd $FRIDAY_DATA/common_voice_single_word \
    && curl https://cdn.commonvoice.mozilla.org/cv-corpus-5.1-singleword/cv-corpus-5.1-singleword.tar.gz > cv_single_word.tar.gz\
    && tar -xvf cv_single_word.tar.gz
```


## FireFox Common Voice Sentences

[common voice](https://commonvoice.mozilla.org/sv-SE/datasets) is a open-source dataset provided by mozilla. 

Run the following commands to Download the Data.

```bash
FRIDAY_DATA=data
mkdir -p $FRIDAY_DATA/common_voice_sentence
cd $FRIDAY_DATA/common_voice_sentence \
    && curl https://voice-prod-bundler-ee1969a6ce8178826482b88e843c335139bd3fb4.s3.amazonaws.com/cv-corpus-5.1-2020-06-22/sv-SE.tar.gz -L > sv-SE.tar.gz \
    && tar -xvf sv-SE.tar.gz
```

## LibriSpeech

[LibriSpeech](http://www.openslr.org/12) is a open ASR dataset.

Run the following commands to Download the Data
```bash
FRIDAY_DATA=data ./scripts/download_librispeech.sh
```
