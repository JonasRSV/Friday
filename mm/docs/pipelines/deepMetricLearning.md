# Deep Metric Learning 

This document describes the entire process of training a DML model from downloading data to exporting model, it has its
own document since it does not fit into the framework of all other models, because this one trains using tripplet loss.

This document will help convert normal ASR datasets into one that is usable for training word embeddings for KWS, it
will do this by creating a 'word-level' dataset using forced alignment.


- [Downloading Dataset](#downloading-dataset)
    - [LibriSpeech](#download-librispeech)
- [Forced Alignment](#forced-alignment)
  - [Downloading](#downloading-mfa)
  - [Aligning Dataset](#aligning-dataset)

### Downloading Dataset

Any dataset that can be force-aligned using the [montreal forced aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/)
is valid. 

#### Download LibriSpeech

See [datasets](../datasets.md) for instructions on downloading LibriSpeech


### Forced Alignment

Too convert our dataset into a DML dataset we need to use a forced aligner, download the [montreal forced aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/)
from its [release page](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases)

#### Downloading MFA

##### Linux 

If you're on linux run: 

```bash
curl -L https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases/download/v1.0.1/montreal-forced-aligner_linux.tar.gz > data/mfa.tar.gz
```

Then open the archive

```bash
cd data && tar -xvf mfa.tar.gz
```

At time of writing [The release failed to include a python.so](https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/issues/109)
so you have to manually symlink the python shared library into the mfa library.

Use the following command to see where your system *.so files are

```bash
sudo ldconfig -p | grep libpython
```

Then a example linking might be

```bash
ln -s /usr/lib/x86_64-linux-gnu/libpython3.6m.so.1.0 montreal-forced-aligner/lib/libpython3.6m.so
```

#### Aligning Dataset

##### LibriSpeech

Assuming it is already downloaded under $FRIDAY_DATA/librispeech as described by [Download Librispeech](#download-librispeech).

Do validation with

```bash
```

Do aligning with

```bash
./data/montreal-forced-aligner/bin/mfa_align \
  ${FRIDAY_DATA}/librispeech/LibriSpeech/train-clean-100/19 \
  ${FRIDAY_DATA}/librispeech/word_phoneme_lexicon.txt \
  data/montreal-forced-aligner/pretrained_models/english \
  ${FRIDAY_DATA}/librispeech/LibriSpeech/train-clean-100-aligned \
  -t /tmp
```
