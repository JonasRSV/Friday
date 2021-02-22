# Query By Examples

QbE (Query by Examples) models take example utterances of keywords and use these for inference. QbE models are evaluated
using one QbE pipeline, results can then be visualized

- [Usage](#usage)
- [Personal Pipeline](#personal-pipeline)
    - [Examples](#personal-examples)
- [Google Speech Commands Pipeline](#google-speech-commands-pipeline)
  - [Examples](#google-speech-examples)
- [Visualize](#visualize)


# Usage

Each model inherits from the abc [model](../../../pipelines/evaluate/query_by_example/model.py). 

## Personal Pipeline

The [personal pipeline](../../../pipelines/evaluate/query_by_example/personal_pipeline.py) is executed with Tasks and Examples.

QbE tasks consists of two parts

1. Task files (See [Record QbE Task](../../tools.md) for how to record)
2. Example files (See [Recording Personal](../../tools.md))

A task file is a tfexample with the following fields

```bash
audio: int64list # a list containing 16bit samples of audio
utterances: byteslist # a list containing '-' separated keywords 'strings' in the order they were uttered.
sample_rate: int64list # a list containing one scalar, the sample_rate of the audio
at_time: int64list #a list of same length at utterances containing information at 'around' what sample the keyword was uttered.
```

A example file is a file of our main format, see [datasets](../../datasets.md)


### Personal Examples
- [jigglypuff](../../models/jigglypuff.md)
- [ditto](../../models/ditto.md)
- [baseline](../../models/random.md)


## Google Speech Commands Pipeline

The [gsc pipeline](../../../pipelines/evaluate/query_by_example/personal_pipeline.py) is executed with the output of
the 'to_examples' [gsc pipeline](../../../pipelines/to_tfexample/google_speech_commands.py)

### Google Speech Examples
- [baseline](../../models/random.md)
- [ditto](../../models/ditto.md)


## Visualize

Each pipeline stores the result in some csv file under 'FRIDAY_DATA'.

See all visualization options with..

```bash
python3 pipelines/evaluate/query_by_example/metrics/visualize.py
```

#### Examples
```bash
FRIDAY_DATA=data python3 pipelines/evaluate/query_by_example/metrics/visualize.py\
  --dataset="P"\
  --visualization="per_distance_accuracy"
```
