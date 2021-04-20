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
    "--eval_prefix=${FRIDAY_SESSION?}/ptfexamples.valid*"\
    --margin=1.0\
    --distance=${BULBASAUR_DISTANCE?}\
    --embedding_dim=512\
    --clip_length=2\
    --model_directory=${MODEL_OUTPUT?}\
    --mode="train_eval"\
    --sample_rate=8000\
    --batch_size=128\
    --start_learning_rate=0.0005\
    --max_steps=1000000\
    --save_summary_every=300\
    --eval_every=300\
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

### Evaluation


Pick a model, it should be a path to a tensorflow 'SavedModel' export directory.

```bash 
BULBASAUR_MODEL=$PWD/data/bulbasaur_model/ddl_apr_6 
```

Then run the evaluate script

```bash
FRIDAY_DATA=data python3 models/bulbasaur/evaluate.py
```

#### Evaluation examples

When evaluating against the 'Personal':

```bash 
FRIDAY_DATA=data python3 models/bulbasaur/evaluate.py\
  --export_dir=${BULBASAUR_MODEL?}\
  --bulbasaur=Simple\
  --pipeline=P\
  --tasks="data/evaluation/tasks/tfexamples.en-easy-jonas-9"\
  --examples="data/evaluation/examples/tfexamples.en*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000
```

When evaluating against 'Google Speech Commands':

```bash 
FRIDAY_DATA=data python3 models/bulbasaur/evaluate.py\
    --export_dir=${BULBASAUR_MODEL?}\
    --bulbasaur=Simple\
    --pipeline=GSC\
    --examples="data/speech_commands_qbe_eval/*"\
    --window_size=2\
    --n=3\
    --seed=1337\
    --sample_rate=8000
```

When evaluating resource usage:

```bash 
FRIDAY_DATA=data python3 models/bulbasaur/evaluate.py\
    --export_dir=${BULBASAUR_MODEL?}\
    --bulbasaur=Simple\
    --pipeline=resource
```

When evaluating usability use:

```bash 
FRIDAY_DATA=data python3 models/bulbasaur/evaluate.py\
    --export_dir=${BULBASAUR_MODEL?}\
    --bulbasaur=Simple\
    --pipeline=usability\
    --examples="data/usability-eval/*"\
    --window_size=2\
    --sample_rate=8000
```


