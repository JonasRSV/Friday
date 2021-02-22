### Random model

A model returning random predictions  


Open [qbe_model](../../models/baseline/qbe_model.py) and uncomment the eval pipeline you want to run.


Evaluate on 'Personal' with

```bash
FRIDAY_DATA=data python3 models/baseline/random_qbe.py\
  --pipeline=P\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000

```

Evaluate on 'Google Speech Commands' with 

```bash
FRIDAY_DATA=data python3 models/baseline/random_qbe.py\
  --pipeline=GSC\
  --examples="data/speech_commands_qbe_eval/*"\
  --window_size=2\
  --n=3\
  --seed=1337\
  --sample_rate=8000
```
