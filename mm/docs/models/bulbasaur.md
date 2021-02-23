# Bulbasaur

![Bulbasaur](bulbasaur/bulbasaur.png)

Bulbasaur is a distance learning model for keyword spotting.

This document explains how to train and evaluate the Bulbasaur keyword spotting model. First set the
model output directory. Bulbasaur depends on the output of the [hash labeling](../pipelines/labeling.md)

```bash
EXPERIMENT_NAME=bulbasaur.$(date | tr " " "_")
MODEL_OUTPUT=/tmp/$EXPERIMENT_NAME
```
