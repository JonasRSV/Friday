
# Jigglypuff

![jigglypuff](jigglypuff/jigglypuff.jpeg)

Jigglypuff is an audio to phonemes model, jigglypuff supports adding custom keywords. Jigglypuff depends on the output
of the [phonemes labeling](../pipelines/labeling.md)

This document explains how to train the Jigglypuff keyword spotting model. First set the
model output directory

```bash
EXPERIMENT_NAME=jigglypuff.$(date | tr " " "_")
MODEL_OUTPUT=/tmp/$EXPERIMENT_NAME
```
Then for training launch

```bash
# Num phonemes + blank + extra labels, is 41 with librispeech dict using phoneme_dict_labeler pipeline
NUM_PHONEMES=41

python3 models/jigglypuff/jigglypuff.py\
    "--train_prefix=${FRIDAY_SESSION?}/ptfexamples.train*"\
    "--eval_prefix=${FRIDAY_SESSION?}/ptfexamples.valid*"\
    --num_phonemes=${NUM_PHONEMES?}\
    --model_directory=$MODEL_OUTPUT\
    --mode="train_eval"\
    --sample_rate=8000\
    --batch_size=32\
    --start_learning_rate=0.0005\
    --max_steps=1000000\
    --save_summary_every=300\
    --eval_every=300\
    --parallel_reads=5
```

To Export after training run
```bash
python3 models/jigglypuff/jigglypuff.py\
    --model_directory=$MODEL_OUTPUT\
    --num_phonemes=${NUM_PHONEMES?}\
    --mode="export"\
    --sample_rate=8000
    
```

### Evaluation

Pick a 'Distance'

```bash
JIGGLYPUFF_DISTANCE=BEAMODTW
JIGGLYPUFF_DISTANCE=ExampleLikelihood
JIGGLYPUFF_DISTANCE=SampleLikelihood
JIGGLYPUFF_DISTANCE=PosteriogramsODTW
```

Pick a model, it should be a path to a tensorflow 'SavedModel' export directory.

```bash 
JIGGLYPUFF_MODEL=$PWD/data/stp_model/1614070522
JIGGLYPUFF_MODEL=$PWD/data/stp_model/stp-no-noise

```

Then run the evaluate script

```bash
FRIDAY_DATA=data python3 models/jigglypuff/evaluate.py
```

#### Evaluation examples

When evaluating against the 'Personal':

```bash 
FRIDAY_DATA=data python3 models/jigglypuff/evaluate.py\
  --export_dir=${JIGGLYPUFF_MODEL?}\
  --jigglypuff=${JIGGLYPUFF_DISTANCE?}\
  --pipeline=P\
  --tasks="data/evaluation/tasks/tfexamples.en-easy-jonas-*"\
  --examples="data/evaluation/examples/tfexamples.en*"\
  --window_size=2.0\
  --window_stride="0.25"\
  --sample_rate=8000
```

When evaluating against 'Google Speech Commands':

```bash 
FRIDAY_DATA=data python3 models/jigglypuff/evaluate.py\
    --export_dir=${JIGGLYPUFF_MODEL?}\
    --jigglypuff=${JIGGLYPUFF_DISTANCE?}\
    --pipeline=GSC\
    --examples="data/speech_commands_qbe_eval/*"\
    --window_size=2\
    --n=3\
    --seed=1337\
    --sample_rate=8000
```

When evaluating resource usage:

```bash 
FRIDAY_DATA=data python3 models/jigglypuff/evaluate.py\
    --export_dir=${JIGGLYPUFF_MODEL?}\
    --jigglypuff=${JIGGLYPUFF_DISTANCE?}\
    --pipeline=resource
```

When evaluating usability use:

```bash 
FRIDAY_DATA=data python3 models/jigglypuff/evaluate.py\
    --export_dir=${JIGGLYPUFF_MODEL?}\
    --jigglypuff=${JIGGLYPUFF_DISTANCE?}\
    --pipeline=usability\
    --examples="data/usability-eval/*"\
    --window_size=2\
    --sample_rate=8000
```

