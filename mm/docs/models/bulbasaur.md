# Bulbasaur

![Bulbasaur](bulbasaur/bulbasaur.png)

Bulbasaur is a distance learning model for keyword spotting.

This document explains how to train and evaluate the Bulbasaur keyword spotting model. First set the
model output directory. Bulbasaur depends on the output of the [hash labeling](../pipelines/labeling.md)

```bash
EXPERIMENT_NAME=bulbasaur.$(date | tr " " "_")
MODEL_OUTPUT=/tmp/$EXPERIMENT_NAME
```

Then for training launch

```bash
python3 models/bulbasaur/bulbasaur.py\
    "--train_prefix=${FRIDAY_SESSION?}/ptfexamples.train*"\
    "--eval_prefix=${FRIDAY_SESSION?}/ptfexamples.valid*"\
    --embedding_dim=256\
    --clip_length=2\
    --model_directory=$MODEL_OUTPUT\
    --mode="train_eval"\
    --sample_rate=8000\
    --batch_size=32\
    --start_learning_rate=0.0005\
    --max_steps=1000000\
    --save_summary_every=200\
    --eval_every=200\
    --parallel_reads=5
```

To Export after training run
```bash
python3 models/bulbasaur/bulbasaur.py\
    --model_directory=$MODEL_OUTPUT\
    --mode="export"\
    --embedding_dim=256\
    --clip_length=2\
    --sample_rate=8000
    
```
