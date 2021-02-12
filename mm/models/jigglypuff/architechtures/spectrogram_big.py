import tensorflow as tf
import sys


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def spectrogram_model_big(x: tf.Tensor,
                          num_phonemes: int,
                          mode: tf.estimator.ModeKeys,
                          regularization: float = 1e-6) -> tf.Tensor:
    print("X", x)
    x = tf.expand_dims(x, -1)
    print("X", x)
    x = tf.compat.v1.layers.Conv2D(filters=64,
                                   kernel_size=(7, 3),
                                   strides=(1, 1),
                                   activation=tf.nn.relu)(x)
    print("X", x)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 3), strides=(1, 1))(x)
    print("X", x)
    x = tf.compat.v1.layers.Conv2D(filters=64,
                                   kernel_size=(1, 7),
                                   activation=tf.nn.relu)(x)
    print("X", x)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 4), strides=(1, 1))(x)
    print("X", x)
    x = tf.compat.v1.layers.Conv2D(filters=128,
                                   kernel_size=(1, 10),
                                   padding="valid",
                                   strides=(1, 2),
                                   activation=tf.nn.relu)(x)
    print("X", x)
    x = tf.compat.v1.layers.Conv2D(filters=256,
                                   kernel_size=(7, 1),
                                   strides=(1, 1),
                                   padding="same",
                                   activation=tf.nn.relu)(x)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 49), strides=(1, 1))(x)
    print("X", x)
    x = tf.compat.v1.layers.Conv2D(filters=128,
                                   kernel_size=(3, 1),
                                   strides=(1, 1),
                                   padding="same",
                                   activation=tf.nn.relu)(x)
    print("X", x)
    logits = tf.compat.v1.layers.Conv2D(filters=num_phonemes,
                                        kernel_size=(1, 1),
                                        activation=None)(x)
    print("X", logits)

    logits = tf.squeeze(logits, axis=2)

    return logits
