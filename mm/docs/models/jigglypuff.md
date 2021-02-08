
# Jigglypuff

![magikarp](jigglypuff/jigglypuff.jpeg)

Jigglypuff is an audio to phonemes model, jigglypuff supports adding custom keywords. 

This document explains how to train the Jigglypuff keyword spotting model. First set the
model output directory

```bash
EXPERIMENT_NAME=jigglypuff.$(date | tr " " "_")
MODEL_OUTPUT=/tmp/$EXPERIMENT_NAME
```

Then for training launch

```bash
python3 models/jigglypuff/jigglypuff.py\
    "--train_prefix=${FRIDAY_SESSION?}/ptfexamples.train*"\
    "--eval_prefix=${FRIDAY_SESSION?}/ptfexamples.valid*"\
    --model_directory=$MODEL_OUTPUT\
    --mode="train_eval"\
    --sample_rate=8000\
    --batch_size=32\
    --start_learning_rate=0.001\
    --max_steps=1000000\
    --save_summary_every=1000\
    --eval_every=1000\
    --parallel_reads=5
```

To Export after training run
```bash
python3 models/jigglypuff/jigglypuff.py\
    --model_directory=$MODEL_OUTPUT\
    --mode="export"\
    --sample_rate=8000
    
```

