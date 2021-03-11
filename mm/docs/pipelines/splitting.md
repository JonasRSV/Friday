#### Splitting

The train_valid_split pipeline creates one train and one validation split.

```bash
python3 pipelines/split.py \
 "--source_prefix=${FRIDAY_SESSION?}/ptfexamples*"\
 --sink_prefix=${FRIDAY_SESSION?}/ptfexamples\
 --examples_per_shard=250\
 --train_fraction=0.995
```
