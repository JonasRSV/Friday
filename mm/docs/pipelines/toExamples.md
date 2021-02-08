- [Common Voice Sentences](#common-voice-sentences)
- [Common Voice Single Word](#common-voice-single-word)
- [Google Speech Commands](#google-speech-commands)
- [LibriSpeech](#librispeech)
- [RecordYourOwnWebsite](#recordyourownwebsite)

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
  --output_prefix=${FRIDAY_SESSION?}/tfexamples.speech_commands\
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
