# Bulbasaur

![Bulbasaur](bulbasaur/bulbasaur.png)

Bulbasaur is a distance learning model for keyword spotting.

This document explains how to train and evaluate the Bulbasaur keyword spotting model. First set the
model output directory. Bulbasaur depends on the output of the ['Deep Metric Learning' labeling](../pipelines/labeling.md)

```bash
EXPERIMENT_NAME=bulbasaur.$(date | tr " " "_")
MODEL_OUTPUT=/tmp/$EXPERIMENT_NAME
```

Then for training, pick a distance

```bash
BULBASAUR_DISTANCE=cosine
BULBASAUR_DISTANCE=euclidean
```

```bash
python3 models/bulbasaur/bulbasaur.py\
    "--train_prefix=${FRIDAY_SESSION?}/ptfexamples.train*"\
    "--eval_prefix=${FRIDAY_SESSION?}/ptfexamples-gsc-valid*"\
    --margin=1.0\
    --distance=${BULBASAUR_DISTANCE?}\
    --embedding_dim=512\
    --clip_length=2\
    --model_directory=${MODEL_OUTPUT?}\
    --mode="train_eval"\
    --sample_rate=8000\
    --batch_size=128\
    --start_learning_rate=0.005\
    --max_steps=1000000\
    --save_summary_every=20\
    --eval_every=20\
    --parallel_reads=5
```

To Export after training run
```bash
python3 models/bulbasaur/bulbasaur.py\
    --model_directory=${MODEL_OUTPUT?}\
    --mode="export"\
    --distance=${BULBASAUR_DISTANCE?}\
    --margin=1.0\
    --embedding_dim=512\
    --clip_length=2\
    --sample_rate=8000
    
```

