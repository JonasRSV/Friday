### Random model

A model returning random predictions  


Evaluating QbE

```bash
python3 models/baseline/qbe_model.py\
  --tasks="data/evaluation/tasks/*"\
  --examples="data/evaluation/examples/*"\
  --window_size=2\
  --window_stride="0.25"\
  --sample_rate=8000

```
