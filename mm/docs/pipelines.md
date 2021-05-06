## Pipelines

### Dependencies

Preprocessing depends on SoX for audio conversion, it is the common voice datasets that needs the mp3 extension for sox.

```bash
sudo apt-get install sox && sudo apt-get libsox-fmt-mp3
```

- [Word Dataset](#word-dataset)
  - [Install MFA](#install-mfa)
  - [LibriSpeech to MFA](#librispeech-to-mfa)
  - [Common Voice to MFA](#common-voice-to-mfa)
  - [Alignment](#alignment)
  - [Alignments To Word Dataset](#alignments-to-word-dataset)
- [Triplet Dataset](#triplet-dataset)

Some environment variables are used

```bash 

FRIDAY_DATA=data
EXPERIMENT_NAME=$(date | tr " " "_")
FRIDAY_SESSION=${FRIDAY_DATA?}/${EXPERIMENT_NAME?}

mkdir -p $FRIDAY_SESSION
```
```


## Word dataset


We create the word dataset from [LibriSpeech](datasets.md) and [Mozilla Common Voice](datasets.md) using [mfa](https://montreal-forced-aligner.readthedocs.io/en/latest/).

### Install MFA

If you're on linux run:

```bash
curl -L https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v1.1.0-beta.2/montreal-forced-aligner_linux.tar.gz > data/mfa.tar.gz
```

Then open the archive

```bash
cd data && tar -xvf mfa.tar.gz
```

If missing a python.so issue occurs you have to manually symlink the python shared library into the mfa library. Use 
the following command to see where your system *.so files are

```bash
sudo ldconfig -p | grep libpython
```

Then an example linking might be

```bash
ln -s /usr/lib/x86_64-linux-gnu/libpython3.6m.so.1.0 montreal-forced-aligner/lib/libpython3.6m.so
```


### LibriSpeech to MFA

Convert LibriSpeech to the input format expected by MFA using

```bash
python3 scripts/librispeech_to_mfa.py \
  --source=${FRIDAY_DATA?}/librispeech/LibriSpeech/train-clean-100\
  --sink=${FRIDAY_DATA?}/mfa_data\
  --prefix=libri-100
  
python3 scripts/librispeech_to_mfa.py \
  --source=${FRIDAY_DATA?}/librispeech/LibriSpeech/train-clean-360\
  --sink=${FRIDAY_DATA?}/mfa_data\
  --prefix=libri-360
```

### Common Voice to MFA

Convert a Common Voice dataset to the input format expected by MFA using

```bash
python3 scripts/common_voice_to_mfa.py \
  --tsv=${FRIDAY_DATA?}/cv-corpus-6.1-2020-12-11/en/validated.tsv \
  --clips=${FRIDAY_DATA?}/cv-corpus-6.1-2020-12-11/en/clips \
  --sink=${FRIDAY_DATA?}/mfa_data\
  --max_per_speaker=50\
  --sample_rate=16000\
  --prefix=cv
```

### Alignment

Run alignment with

```bash
./data/montreal-forced-aligner/bin/mfa_align \
  ${FRIDAY_DATA?}/mfa_data \
  ${FRIDAY_DATA?}/librispeech/word_phoneme_lexicon.txt \
  data/montreal-forced-aligner/pretrained_models/english.zip \
  ${FRIDAY_DATA?}/mfa_data_aligned \
  -t /tmp
```

The phoneme lexicon can be found on the [mfa](https://montreal-forced-aligner.readthedocs.io/en/latest/) website


### MFA Alignments to Word Dataset

```bash
python3 pipelines/mfa_alignments_to_words_dataset.py\
  --audio=${FRIDAY_DATA?}/mfa_data \
  --alignments=${FRIDAY_DATA?}/mfa_data_aligned \
  --sink=${FRIDAY_DATA?}/words_dataset \
  --sample_rate=16000 \
  --min_word_length=5 \
  --min_occurrences=5 
```



## Triplet dataset

We create the triplet dataset from the [Word dataset](#word-dataset).


```bash
python3 pipelines/triplization.py\
  --source=${FRIDAY_DATA?}/words_dataset \
  --sink_prefix=${FRIDAY_SESSION?}/ptfexamples-dml-1 \
  --sample_rate=16000 \
  --clip_length=2 \
  --augmentations\
  --expected_file_size=250 \
  --expected_total_size=100000
  
```




