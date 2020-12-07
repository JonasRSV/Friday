## Goldfish Preprocessing

- [Common Voice](#common-voice)
- [Google Speech Commands](#google-speech-commands)
- [Common Pipelines](#common-pipelines)


### Dependencies

Preprocessing depends on SoX for audio conversion, it is the common voice datasets that needs the mp3 extension for sox.

```bash
sudo apt-get install sox && sudo apt-get libsox-fmt-mp3
```

Some environment variables are used 

```bash 
FRIDAY_DATA=data
EXPERIMENT_NAME=$(date | tr " " "_")
FRIDAY_SESSION=${FRIDAY_DATA?}/${EXPERIMENT_NAME?}
```

### Common Voice Sentences

Create current session

```bash
mkdir -p ${FRIDAY_SESSION}
```

Create common format from firefox common voice sentences using:

```bash
python3 pipelines/firefox_common_voice.py 
  --tsv=${FRIDAY_DATA?}/common_voice_sentences/cv-corpus-5.1-2020-06-22/sv-SE/validated.tsv \
  --clips=${FRIDAY_DATA?}/common_voice_sentences/cv-corpus-5.1-2020-06-22/sv-SE/clips \
  --output_prefix=${FRIDAY_SESSION?}/tfexamples.cv_long\
  --sample_rate=8000
```

#### Common Voice Single Word

Create current session

```bash
mkdir -p ${FRIDAY_SESSION}
```
Pick a language, to see alternatives use:

```bash
ls data/common_voice_single_word/cv-corpus-5.1-singleword
```

```bash
LANGUAGE=en
```

Create common format from firefox common voice words using:

```bash
python3 pipelines/firefox_common_voice.py \
  --tsv=${FRIDAY_DATA?}/common_voice_single_word/cv-corpus-5.1-singleword/${LANGUAGE?}/validated.tsv \
  --clips=${FRIDAY_DATA?}/common_voice_single_word/cv-corpus-5.1-singleword/${LANGUAGE?}/clips \
  --sample_rate=8000\
  --output_prefix=${FRIDAY_SESSION?}/tfexamples.common_voice_single_word
```

### Google Speech Commands

```bash
mkdir -p ${FRIDAY_SESSION}
```

Create common format from Google Speech Commands

```bash
python3 pipelines/google_speech_commands.py \
  --base_path=${FRIDAY_DATA?}/google_speech_commands \
  --output_prefix=${FRIDAY_SESSION?}/tfexamples.speech_commands\
  --sample_rate=8000
```


### Common Pipelines

#### Preprocessing

This pipeline adds labels and standardizes the data

```bash
LABEL_MAP_PATH=${PWD}/resources/class_maps/google_speech_commands_label_map.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/google_speech_commands_few_label_map.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/tänd_släck.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/kombination.json


python3 pipelines/preprocess.py \
 "--source=${FRIDAY_SESSION?}/tfexamples*"\
  --sink_prefix=${FRIDAY_SESSION?}/ptfexamples\
  --label_map_path=${LABEL_MAP_PATH?}\
  --maximum_clip_length=2
```

After this pipeline run the within file shuffling

### Shuffling

```bash
python3 pipelines/shuffle.py "--source=${FRIDAY_SESSION?}/ptfexamples*"
```

After this pipeline run the splitting

#### Splitting

The train_valid_split pipeline creates one train and one validation split.

```bash
python3 pipelines/split.py \
 "--source_prefix=${FRIDAY_SESSION?}/ptfexamples*"\
 --sink_prefix=${FRIDAY_SESSION?}/ptfexamples\
 --examples_per_shard=100\
 --train_fraction=0.8
```

Once this is done you can train a model - See arbitrary model documentation for that.
