# Ditto

![ditto](ditto/ditto.png)
 
Ditto is a model using audio matching algorithms for QbE KWS. It is basically DTW.


- [Evaluation](#evaluation)

### Evaluation


There are many ditto variants, open [evaluate](../../models/ditto/evaluate.py) and uncomment all but the one you want 
to evaluate.

When evaluating against the personal pipeline, use:

```bash
python3 models/ditto/evaluate.py\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000
```

When evaluating against google speech commands use:

```bash 
python3 models/ditto/evaluate.py\
    --examples="data/speech_commands_qbe_eval/*"\
    --window_size=2\
    --n=3\
    --seed=1337\
    --sample_rate=8000
```