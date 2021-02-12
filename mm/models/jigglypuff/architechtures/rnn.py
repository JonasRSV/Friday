import tensorflow as tf
import sys


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def rnn(x: tf.Tensor,
        num_phonemes: int,
        mode: tf.estimator.ModeKeys,
        regularization: float = 1e-6) -> tf.Tensor:

    cells = [
        tf.contrib.rnn.LSTMCell(512),
        tf.contrib.rnn.LSTMCell(512),
        tf.contrib.rnn.LSTMCell(num_phonemes, activation=None)
    ]
    # The second output is the last state and we will no use that
    logits = tf.keras.layers.RNN(cells, return_sequences=True)(x, training=mode == tf.estimator.ModeKeys.TRAIN)

    return logits
