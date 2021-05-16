# MM 

---

- [Procedure](#procedure)
- [Architecture](#architechture)

MM stands for Model Making

This folder contains code for training the **deep distance learning** model used by friday.

## Procedure


Start with creating a virutalenv and install all requirements

```bash
virtualenv -p python3 .venv && pip3 install -r requirements.txt
```

To train a model

1. Download as many dataset as possible (see [docs/datasets](docs/datasets))
2. Construct a words dataset from them (see [docs/pipelines.md](docs/pipelines.md))
3. Construct a triplet dataset from a words dataset (see [docs/pipelines.md](docs/pipelines.md))
4. Shuffle and split the words dataset (see [docs/shuffling.md](docs/shuffling.md) and [docs/splitting.md](docs/splitting.md))
5. Train and export a model (see [docs/models/bulbasaur.md](docs/models/bulbasaur.md))

To inspect files created in steps 2 and 3 use [docs/tools.md](docs/tools.md)


## Architecture

These can be found in [models/bulbasaur/architechtures/kaggle.py](models/bulbasaur/architechtures/kaggle.py). The current arch is inspired by a [kaggle speech recognition submission](https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715). The arch seem to work fairly well for the distance learning task, but contributions with better archs are most welcome. 

The current arch reaches a (validation/train) loss of around 60 after 200k steps.

