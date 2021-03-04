import tensorflow as tf


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def projection_head(x: tf.Tensor,
                    embedding_dim: int,
                    mode: tf.estimator.ModeKeys,
                    regularization: float = 1e-6) -> tf.Tensor:
    with tf.variable_scope('projection_head', reuse=tf.AUTO_REUSE):
        x = tf.compat.v1.layers.Dense(embedding_dim, activation="relu", name="projection_head_1")(x)
        x = tf.compat.v1.layers.Dense(embedding_dim, activation="relu", name="projection_head_2")(x)
        embedding = tf.compat.v1.layers.Dense(embedding_dim, activation=None, name="projection_head_3")(x)

    return embedding
