# Labeling


## One class per clip

This pipeline adds labels using a label map, and standardizes the data.

```bash
LABEL_MAP_PATH=${PWD}/resources/class_maps/google_speech_commands_label_map.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/google_speech_commands_few_label_map.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/tänd_släck.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/kombination.json
LABEL_MAP_PATH=${PWD}/resources/class_maps/firefox_common_voice_en_single_word.json


python3 pipelines/preprocess.py \
 "--source=${FRIDAY_SESSION?}/tfexamples*"\
  --sink_prefix=${FRIDAY_SESSION?}/ptfexamples\
  --label_map_path=${LABEL_MAP_PATH?}\
  --maximum_clip_length=2
```

## Phonemes

This pipelines adds labels using a word to phoneme dictionary

```bash
PHONEME_DICTIONARY_PATH=${FRIDAY_DATA?}/librispeech/word_phoneme_lexicon.txt

python3 pipelines/preprocess_phoneme.py \
 "--source=${FRIDAY_SESSION?}/tfexamples*"\
  --sink_prefix=${FRIDAY_SESSION?}/ptfexamples\
  --phoneme_dictionary_path=${PHONEME_DICTIONARY_PATH?}
```