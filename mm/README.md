# MM 

---

MM stands for Model Making

This contains code for training the **deep distance learning** model used by friday.

To train one yourself:

1. Download as many dataset as possible (see docs/datasets)
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


