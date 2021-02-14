import tensorflow as tf
import sys


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def rnn(x: tf.Tensor,
        num_phonemes: int,
        mode: tf.estimator.ModeKeys,
        regularization: float = 1e-6) -> tf.Tensor:

    print("x", x.shape)

    cells = [
        tf.contrib.rnn.LSTMCell(128),
        tf.contrib.rnn.LSTMCell(128),
        tf.contrib.rnn.LSTMCell(128),
    ]
    # The second output is the last state and we will no use that
    x = tf.keras.layers.RNN(cells, return_sequences=True)(x, training=mode == tf.estimator.ModeKeys.TRAIN)
    print("x", x)
    x = tf.keras.layers.Dense(128, activation='tanh')(x)
    print("x", x)
    logits = tf.keras.layers.Dense(num_phonemes, activation=None)(x)


    print("logits", logits)

    return logits
