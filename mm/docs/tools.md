# Docs for shared tools

- [Inspect](#Inspect)
- [Recording Personal](#Recording Personal)

---

## Inspect 

---

To inspect that the tfexamples contains valid voice data one can use e.g

```bash
python3 tools/friday_inspect.py \
 --path=${FRIDAY_SESSION?}/EXAMPLE_FILE_HERE \
 --mode=play_audio
```

Play with augmentation

```bash
python3 tools/friday_inspect.py \
 --path=${FRIDAY_SESSION?}/EXAMPLE_FILE_HERE \
 --mode=play_augmented_audio
```

Plot audio signal
```bash
python3 tools/friday_inspect.py \
 --path=${FRIDAY_SESSION?}/EXAMPLE_FILE_HERE \
 --mode=visualize

```

To show just meta information use

```bash 

python3 tools/friday_inspect.py \
 --path=${FRIDAY_SESSION?}/EXAMPLE_FILE_HERE \
 --mode=meta
```

To count labels use

```bash 
python3 tools/friday_inspect.py \
 --path="${FRIDAY_SESSION?}/ptfexamples.train*" \
 --mode=count_labels
```

To play a random file of a specific text

```bash 
python3 tools/friday_inspect.py \
 --path="${FRIDAY_SESSION?}/ptfexamples.train*" \
 --mode=play_random\
 --arg="släck ljuset"
```

## Recording Personal

---

This assumes FRIDAY_SESSION is set, replace --text with the text you will be saying.

Once the program starts, you press enter then you have 'clip_length' e.g 2 seconds time to speak the text. After you have spoken it will be
repeated to you. Then press enter when you're ready to speak the same text again and repeat. Each time you press enter it will record for 2 seconds then play it back.
Once you're done, do one keyboard interrupt and it will save your recordings into the common format.

```bash
TEXT="godmorgon"

# use arecord -L to list devices

DEVICE="default"

python3 tools/record_personal_examples.py\
    --file_prefix=${FRIDAY_SESSION?}/tfexamples\
    --sample_rate=8000\
    --clip_length=2.0\
    --text=${TEXT?}\
    --device=${DEVICE?}

```

Recording background noise
```bash

# use arecord -L to list devices
DEVICE="default"

python3 tools/record_personal_examples.py\
    --file_prefix=${FRIDAY_SESSION?}/tfexamples\
    --sample_rate=8000\
    --clip_length=2.0\
    --text=""\
    --background="[UNK]"\
    --device=${DEVICE?}
```


### Manually filtering a record

If you when for example recorded your own data made a mistake and said the wrong word, you can use this to
drop examples from the record.

```bash
INPUT_FILE=...
OUTPUT_FILE=...

python3 tools/manually_filter_records.py\
 --input_file=${INPUT_FILE?} \
 --output_file=${OUTPUT_FILE?}
```
