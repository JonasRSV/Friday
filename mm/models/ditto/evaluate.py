import os
import sys

# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import model_fastdtw
import model_fastdtw_mfcc
import model_dtw_mfcc
import model_odtw_mfcc

from pipelines.evaluate.query_by_example.personal_pipeline import run as personal_run
from pipelines.evaluate.query_by_example.google_speech_commands_pipeline import run as google_run
from pipelines.evaluate.query_by_example.metrics.google_speech_commands.accuracy import per_class_accuracy


def run_google_speech_commands_pipeline(model):
    confusion_block, keywords, all_keywords = google_run(model, keywords=["sheila", "wow", "visual"])
    print(confusion_block)
    per_class_accuracy(confusion_block, keywords)


def run_personal_pipeline(model):
    personal_run(model)


if __name__ == "__main__":
    # personal_run(model_fastdtw.FastDTW(max_distance=2000000))
    # personal_run(model_fastdtw_mfcc.FastDTWMFCC(max_distance=1900))
    # personal_run(model_dtw_mfcc.DTWMFCC(max_distance=2050))
    # personal_run(model_odtw_mfcc.ODTWMFCC(max_distance=2050))

    # run_google_speech_commands_pipeline(model_fastdtw.FastDTW(max_distance=2000000))
    # run_google_speech_commands_pipeline(model_fastdtw_mfcc.FastDTWMFCC(max_distance=1900))
    # run_google_speech_commands_pipeline(model_dtw_mfcc.DTWMFCC(max_distance=2050))
    run_google_speech_commands_pipeline(model_odtw_mfcc.ODTWMFCC(max_distance=2600))
