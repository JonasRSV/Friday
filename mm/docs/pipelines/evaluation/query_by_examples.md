# Query By Examples

QbE (Query by Examples) models take example utterances of keywords and use these for inference. QbE models are evaluated
using the QbE pipeline. 

- [Usage](#usage)
- [QbE dataset](#qbe-dataset)
- [Examples](#examples)

### Usage

Each model inherits from the abc [model](../../../pipelines/evaluate/query_by_example/model.py). Then the
[pipeline](../../../pipelines/evaluate/query_by_example/pipeline.py) can be ran with a [QbE dataset](#qbe-dataset).

### QbE dataset

A QbE dataset consists of two parts

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


### Examples
[jigglypuff](../../models/jigglypuff.md)

