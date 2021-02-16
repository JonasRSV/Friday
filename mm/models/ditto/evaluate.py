import os
import sys
# Some systems don't use the launching directory as root
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import model_fastdtw
import model_fastdtw_mfcc
import model_dtw_mfcc

from pipelines.evaluate.query_by_example.pipeline import run

if __name__ == "__main__":
    #run(model_fastdtw.FastDTW(max_distance=2000000))
    run(model_fastdtw_mfcc.FastDTWMFCC(max_distance=1900))
    #run(model_dtw_mfcc.DTWMFCC(max_distance=1950))

