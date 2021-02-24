import tensorflow as tf


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def projection_head(x: tf.Tensor,
                    embedding_dim: int,
                    mode: tf.estimator.ModeKeys,
                    regularization: float = 1e-6) -> tf.Tensor:
    with tf.variable_scope('projection_head', reuse=tf.AUTO_REUSE):
        x = tf.compat.v1.layers.Dense(embedding_dim, activation="relu")(x)
        embedding = tf.compat.v1.layers.Dense(embedding_dim, activation=None)(x)

    return embedding
