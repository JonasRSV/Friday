# MM 

---


MM stands for Model Making

This folder contains code for training the **deep distance learning** model used by friday.

## Usage


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

