# MM 

---

MM stands for model making - the general flow is as follows

1. Datasets are downloaded (see docs/datasets.md)
2. Datasets are converted to a common format (see docs/pipelines.md)
3. Common format is preprocessed (see docs/pipelines.md)
4. Splitting (see docs/pipelines.md)
5. Model is trained (see docs/models)
5. Model is exported to a representation usable by friday (see docs/models)

There are also tools for inspecting the common data representation (see docs/tools.md) and tools for adding your own recordings to the data with your own labels (docs/tools.md).

## Developing

Use a virtualenv

```bash
virtualenv -p python3 .venv && pip3 install -r requirements.txt
```

See docs/ for how to run things


