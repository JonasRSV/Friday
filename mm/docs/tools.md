# Docs for shared tools

### Inspect 

To play random triplets to verify their content use:

```bash
python3 tools/friday_inspect_dml.py \
  --prefix=${FRIDAY_SESSION?}
```
To play audio files from words dataset use

```bash
python3 tools/friday_inspect_words.py \
  --prefix=${FRIDAY_DATA?}/words_dataset \
  --augment
```
