## Pipelines

### Dependencies

Preprocessing depends on SoX for audio conversion, it is the common voice datasets that needs the mp3 extension for sox.

```bash
sudo apt-get install sox && sudo apt-get libsox-fmt-mp3
```

Some environment variables are used

```bash 
FRIDAY_DATA=data
EXPERIMENT_NAME=$(date | tr " " "_")
FRIDAY_SESSION=${FRIDAY_DATA?}/${EXPERIMENT_NAME?}

mkdir -p $FRIDAY_SESSION
```

For converting some dataset into the common format, see [ToExamples](pipelines/toExamples.md). For Adding labels, 
phonemes or classes see [labeling](pipelines/labeling.md). For postprocessing such as shuffling, splitting see 
corresponding pipelines/xxx file.
