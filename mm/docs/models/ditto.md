# Ditto

![ditto](ditto/ditto.png)
 
Ditto is a model using audio matching algorithms for QbE KWS. It is basically DTW.


- [Evaluation](#evaluation)

### Evaluation


There are many ditto variants, first pick one to evaluate.

```bash
DITTO_MODEL=DTWMFCC
DITTO_MODEL=ODTWMFCC
```

Then,

When evaluating against the 'Personal':

```bash 
FRIDAY_DATA=data python3 models/ditto/evaluate.py\
  --ditto=${DITTO_MODEL?}\
  --pipeline=P\
  --tasks="data/evaluation/tasks/tfexamples.en-hard-jonas-*"\
  --examples="data/evaluation/examples/tfexamples.en*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000
```

When evaluating against 'Google Speech Commands':

```bash 
FRIDAY_DATA=data python3 models/ditto/evaluate.py\
    --ditto=${DITTO_MODEL?}\
    --pipeline=GSC\
    --examples="data/speech_commands_qbe_eval/*"\
    --window_size=2\
    --n=3\
    --seed=1337\
    --sample_rate=8000
```

When evaluating resource usage:

```bash 
FRIDAY_DATA=data python3 models/ditto/evaluate.py\
    --ditto=${DITTO_MODEL?}\
    --pipeline=resource
```

When evaluating usability use:

```bash 
FRIDAY_DATA=data python3 models/ditto/evaluate.py\
    --ditto=${DITTO_MODEL?}\
    --pipeline=usability\
    --examples="data/usability-eval/*"\
    --window_size=2\
    --sample_rate=8000
```
