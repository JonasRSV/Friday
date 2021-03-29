- [Common Voice Sentences](#common-voice-sentences)
- [Common Voice Single Word](#common-voice-single-word)
- [Google Speech Commands](#google-speech-commands)
- [LibriSpeech](#librispeech)
- [RecordYourOwnWebsite](#recordyourownwebsite)
- [ASR to Word](#asr-to-word)

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
python3 pipelines/to_tfexample/firefox_common_voice.py \
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
python3 pipelines/to_tfexample/google_speech_commands.py \
  --base_path=${FRIDAY_DATA?}/google_speech_commands \
  --output_prefix=${FRIDAY_SESSION?}/tfexamples.\
  --sample_rate=8000
```

### LibriSpeech

```bash
mkdir -p ${FRIDAY_SESSION}
```

Create common format from LibriSpeech

```bash
python3 pipelines/to_tfexample/librispeech.py \
   -libri_root=${FRIDAY_DATA?}/librispeech/LibriSpeech\
   -output_prefix=${FRIDAY_SESSION?}/tfexamples.librispeech\
   --sample_rate=8000
```

### RecordYourOwnWebsite

To convert samples produced by [RecordYourOwnWebsite](https://github.com/JonasRSV/Friday/tree/main/web/recordyourownsite) use the following:

```bash
python3 pipelines/to_tfexample/record_your_own_website.py \
 --source=${FRIDAY_ROOT?}/web/recordyourownsite/recordings\
 --sink=$PWD/data/unverified\
 --sample_rate=8000
```

### ASR to Word

By using forced alignment we can create word datasets from ASR datasets. It involves quite a few steps but here goes:

Any dataset that can be force-aligned using the [montreal forced aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/)
is usable with ASR to Word, for example [librispeech](#librispeech). First we need to convert the dataset into the MFA
format

For example for librispeech:

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

Then we use the MFA forced aligner, begin with downloading it [montreal forced aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/)
from its [release page](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases)

##### Linux

If you're on linux run:

```bash
curl -L https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v1.1.0-beta.2/montreal-forced-aligner_linux.tar.gz > data/mfa.tar.gz
```

Then open the archive

```bash
cd data && tar -xvf mfa.tar.gz
```

If [missing a python.so issue](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/issues/109)
occurs you have to manually symlink the python shared library into the mfa library.

Use the following command to see where your system *.so files are

```bash
sudo ldconfig -p | grep libpython
```

Then an example linking might be

```bash
ln -s /usr/lib/x86_64-linux-gnu/libpython3.6m.so.1.0 montreal-forced-aligner/lib/libpython3.6m.so
```

Once downloaded alignin a mfa dataset with

```bash
./data/montreal-forced-aligner/bin/mfa_align \
  ${FRIDAY_DATA}/mfa_data \
  ${FRIDAY_DATA}/librispeech/word_phoneme_lexicon.txt \
  data/montreal-forced-aligner/pretrained_models/english.zip \
  ${FRIDAY_DATA}/mfa_data_aligned \
  -t /tmp
```

Then convert into common format with the following script, before running it make sure you max out your systems allowed
open file handles: See https://access.redhat.com/solutions/61334 for how to do it. You need at least around 20K handles
the reason for this hacky solution is to preserve performance. [TFRecords does not support appending to files](https://github.com/tensorflow/tensorflow/issues/31738) so
to avoid taking a performance hit the workaround is to open all files at once.. which means one file per word. 

```bash
python3 pipelines/to_tfexample/montreal_forced_aligner.py \
  --alignments=${FRIDAY_DATA?}/mfa_data_aligned \
  --audio=${FRIDAY_DATA?}/mfa_data\
  --sink=${FRIDAY_SESSION?} \
  --min_occurrences=10 \
  --min_word_length=3 \
  --target_occurrences=100 
```

This script takes quite some time, if you stop it mid-way use 

```bash
python3 scripts/remove_truncated_records.py --source=${FRIDAY_SESSION?} 
```

to remove corrupted records.