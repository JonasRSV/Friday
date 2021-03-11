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

This pipelines adds labels using a word to phoneme dictionary.

```bash
PHONEME_DICTIONARY_PATH=${FRIDAY_DATA?}/librispeech/word_phoneme_lexicon.txt

python3 pipelines/preprocess_phoneme.py \
 "--source=${FRIDAY_SESSION?}/tfexamples*" \
  --sink_prefix=${FRIDAY_SESSION?}/ptfexamples \
  --phoneme_dictionary_path=${PHONEME_DICTIONARY_PATH?}\
  --expected_output_file_size=100\
  --maximum_clip_length=20 
```

## Hash

This pipeline adds labels based on a hash of the text.

```bash
python3 pipelines/preprocess_hash.py \
 "--source=${FRIDAY_SESSION?}/tfexamples*" \
  --sink_prefix=${FRIDAY_SESSION?}/ptfexamples \
  --expected_output_file_size=100\
  --maximum_clip_length=2\
  --chunk_stride=2
```

## Deep Metric Learning

This pipeline creates a new kind of tfexample

```python3
# The audio fields are x seconds recordings of mono 16 bit PCM data 

anchor: int64list # Anchor audio recording
positive: int64list # Positive audio recording
negative: int64list # Negative audio recording


anchor_text:  byteslist # The text content of the anchor audio recording
positive_text:  byteslist # The text content of the positive audio recording (probably equal to anchor text)
negative_text:  byteslist # The text content of the negative audio recording 

sample_rate: int64 # This should pretty much always be 8kHz or 16kHz
```

This pipeline operates on tfexamples of the 'common format' that follows the following naming convention "tfexamples.$UTTERANCE.*"
meaning files should contain in the name the kind of recordings they contain. This pipeline will then sample triples
from such a dataset until the target dataset reaches a provided size.

```bash
python3 pipelines/preprocess_dml.py \
  --source=${FRIDAY_SESSION?} \
  --sink_prefix=${FRIDAY_SESSION}/ptfexamples \
  --expected_file_size=500 \
  --expected_total_size=150000 \
  --samples_per_instance=5 
```
