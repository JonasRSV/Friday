# Docs for shared tools

- [Inspect](#Inspect)
  - [Inspect DML](#inspect-dml)
- [Recording Personal](#Recording-Personal)
- [Manually Filtering a Record](#manually-filtering-a-record)
- [Convert Text of a collection of record](#convert-text-of-a-collection-of-record)
- [Record QbE task](#record-qbe-task)

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

To get longest audio length and longest phoneme length

```bash 
python3 tools/friday_inspect.py \
 --path="${FRIDAY_SESSION?}/ptfexamples*" \
 --mode=sequence_lengths
```

### Inspect DML

To play random DML triplets to verify their content use:

```bash
python3 tools/friday_inspect_dml.py \
  --prefix=${FRIDAY_SESSION?}
```

## Recording Personal

---

This assumes FRIDAY_SESSION is set, replace --text with the text you will be saying.

Once the program starts, you press enter then you have 'clip_length' e.g 2 seconds time to speak the text. After you have spoken it will be
repeated to you. Then press enter when you're ready to speak the same text again and repeat. Each time you press enter it will record for 2 seconds then play it back.
Once you're done, do one keyboard interrupt and it will save your recordings.

```bash
TEXT="godmorgon"

# use arecord -L to list devices

DEVICE="default"

python3 tools/record/record_personal_examples.py\
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

python3 tools/record/record_personal_examples.py\
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

### Convert Text of a collection of record

```bash
python3 tools/convert_text.py\
  --input_directory=data/personal_recordings\
  --output_directory=data/tmp\
  --convert_from="god natt"\
  --convert_to="godnatt"
```

### Record QbE task 

```bash
python3 tools/record/record_qbe_task.py\
  --sample_rate=8000
```