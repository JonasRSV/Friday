### Random model

A model returning random predictions  


Open [qbe_model](../../models/baseline/qbe_model.py) and uncomment the eval pipeline you want to run.


For personal exec this command

```bash
python3 models/baseline/qbe_model.py\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000

```

For google speech commands exec this command

```bash
python3 models/baseline/qbe_model.py\
  --examples="data/speech_commands_qbe_eval/*"\
  --window_size=2\
  --n=3\
  --seed=1337\
  --sample_rate=8000
```
