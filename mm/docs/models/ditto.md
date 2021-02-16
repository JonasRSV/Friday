# Ditto

![ditto](ditto/ditto.png)
 
Ditto is a model using audio matching algorithms for QbE KWS. It is inspired by DTW.


- [Evaluation](#evaluation)
    - [Fast DTW](#dtw)
    - [DTW](#dtw)
    - [DTW + MFCC](#dtw--mfcc)

### Evaluation

This shows how to run the QbE KWS evaluation pipeline with ditto.

#### Fast DTW

Open [evaluate](../../models/ditto/evaluate.py) and add 'run' FastDTW, then launch evaluation with

```bash
python3 models/ditto/evaluate.py\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000
```

#### Fast DTW + MFCC

Open [evaluate](../../models/ditto/evaluate.py) and uncomment 'FastDTWMFCC', then launch evaluation with

```bash
python3 models/ditto/evaluate.py\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000
```

#### DTW + MFCC

