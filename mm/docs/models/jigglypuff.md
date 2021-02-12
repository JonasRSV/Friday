
# Jigglypuff

![magikarp](jigglypuff/jigglypuff.jpeg)

Jigglypuff is an audio to phonemes model, jigglypuff supports adding custom keywords. 

This document explains how to train the Jigglypuff keyword spotting model. First set the
model output directory

```bash
EXPERIMENT_NAME=jigglypuff.$(date | tr " " "_")
MODEL_OUTPUT=/tmp/$EXPERIMENT_NAME
```

To calculate max_label_sequence_length use
```bash
python3 tools/friday_inspect.py \
 --path="${FRIDAY_SESSION?}/ptfexamples*" \
 --mode=sequence_lengths
```

the second number is the max_label_sequence_length

Then for training launch

```bash
# For librispeech with phoneme_dict_labeler pipeline
MAX_LABEL_SEQUENCE_LENGTH=618
MAX_AUDIO_SEQUENCE_LENGTH=160000
# Num phonemes + blank + extra labels, is 41 with librispeech dict using phoneme_dict_labeler pipeline
NUM_PHONEMES=41

python3 models/jigglypuff/jigglypuff.py\
    "--train_prefix=${FRIDAY_SESSION?}/ptfexamples.train*"\
    "--eval_prefix=${FRIDAY_SESSION?}/ptfexamples.valid*"\
    --max_audio_sequence_length=${MAX_AUDIO_SEQUENCE_LENGTH}\
    --max_label_sequence_length=${MAX_LABEL_SEQUENCE_LENGTH?}\
    --num_phonemes=${NUM_PHONEMES?}\
    --model_directory=$MODEL_OUTPUT\
    --mode="train_eval"\
    --sample_rate=8000\
    --batch_size=20\
    --start_learning_rate=0.0005\
    --max_steps=1000000\
    --save_summary_every=5\
    --eval_every=5\
    --parallel_reads=5
```

To Export after training run
```bash
python3 models/jigglypuff/jigglypuff.py\
    --model_directory=$MODEL_OUTPUT\
    --mode="export"\
    --sample_rate=8000
    
```

