#! /bin/bash

# Crash if errors occur
set -e

if [ -z "$FRIDAY_DATA" ]
  then
    echo "Please set FRIDAY_DATA"
    exit 1
  else
    echo "Downloading into $FRIDAY_DATA"
fi

if test -d "$FRIDAY_DATA/librispeech/LibriSpeech"; then
  echo "$FRIDAY_DATA/librispeech/LibriSpeech exists.. Downloading nothing.."
else
  echo "Creating $FRIDAY_DATA/librispeech"
  mkdir -p $FRIDAY_DATA/librispeech

  if test -f "$FRIDAY_DATA/librispeech/train-1.tar.gz"; then
      echo "$FRIDAY_DATA/librispeech/train-1.tar.gz exists... skipping"
  else
    echo "Downloading first part of train to $FRIDAY_DATA/librispeech/train-1.tar.gz"
    curl https://www.openslr.org/resources/12/train-clean-100.tar.gz > $FRIDAY_DATA/librispeech/train-1.tar.gz
  fi

  if test -f "$FRIDAY_DATA/librispeech/train-2.tar.gz"; then
      echo "$FRIDAY_DATA/librispeech/train-2.tar.gz exists... skipping"
  else
    echo "Downloading second part of train to $FRIDAY_DATA/librispeech/train-2.tar.gz"
    curl https://www.openslr.org/resources/12/train-clean-360.tar.gz > $FRIDAY_DATA/librispeech/train-2.tar.gz
  fi

  if test -f "$FRIDAY_DATA/librispeech/train-3.tar.gz"; then
      echo "$FRIDAY_DATA/librispeech/train-3.tar.gz exists... skipping"
  else
    echo "Downloading third part of train to $FRIDAY_DATA/librispeech/train-3.tar.gz"
    curl https://www.openslr.org/resources/12/train-other-500.tar.gz > $FRIDAY_DATA/librispeech/train-3.tar.gz
  fi

  if test -f "$FRIDAY_DATA/librispeech/test-1.tar.gz"; then
      echo "$FRIDAY_DATA/librispeech/test-1.tar.gz exists... skipping"
  else
    echo "Downloading first part of test to $FRIDAY_DATA/librispeech/test-1.tar.gz"
    curl https://www.openslr.org/resources/12/test-clean.tar.gz > $FRIDAY_DATA/librispeech/test-1.tar.gz
  fi

  if test -f "$FRIDAY_DATA/librispeech/test-2.tar.gz"; then
      echo "$FRIDAY_DATA/librispeech/test-2.tar.gz exists... skipping"
  else
    echo "Downloading first part of test to $FRIDAY_DATA/librispeech/test-2.tar.gz"
    curl https://www.openslr.org/resources/12/test-other.tar.gz > $FRIDAY_DATA/librispeech/test-2.tar.gz
  fi
fi

if test -f "$FRIDAY_DATA/librispeech/word_phoneme_lexicon.txt"; then
    echo "$FRIDAY_DATA/librispeech/word_phoneme_lexicon.txt exists... skipping"
else
  echo "Downloading word_phoneme_lexicon $FRIDAY_DATA/librispeech/word_phoneme_lexicon.txt"
  curl http://www.openslr.org/resources/11/librispeech-lexicon.txt > $FRIDAY_DATA/librispeech/word_phoneme_lexicon.txt
fi
