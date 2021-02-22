# Ditto

![ditto](ditto/ditto.png)
 
Ditto is a model using audio matching algorithms for QbE KWS. It is basically DTW.


- [Evaluation](#evaluation)

### Evaluation


There are many ditto variants, first pick one to evaluate.

```bash
DITTO_MODEL=FASTDTW
DITTO_MODEL=FASTDTWMFCC
DITTO_MODEL=DTWMFCC
DITTO_MODEL=ODTWMFCC
```

Then,

When evaluating against the 'Personal':

```bash 
FRIDAY_DATA=data python3 models/ditto/evaluate.py\
  --ditto=${DITTO_MODEL?}\
  --pipeline=P\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
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