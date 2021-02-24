import tensorflow as tf


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def kaggle_cnn(x: tf.Tensor,
               embedding_dim: int,
               mode: tf.estimator.ModeKeys,
               regularization: float = 1e-6) -> tf.Tensor:
    with tf.variable_scope('kaggle_cnn', reuse=tf.AUTO_REUSE):
        x = tf.expand_dims(x, -1)
        x = tf.compat.v1.layers.Conv2D(filters=64,
                                       kernel_size=(7, 3),
                                       activation=tf.nn.relu)(x)
        x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 3), strides=(1, 1))(x)
        x = tf.compat.v1.layers.Conv2D(filters=128,
                                       kernel_size=(1, 7),
                                       activation=tf.nn.relu)(x)
        x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 4), strides=(1, 1))(x)
        x = tf.compat.v1.layers.Conv2D(filters=256,
                                       kernel_size=(1, 10),
                                       padding="valid",
                                       activation=tf.nn.relu)(x)
        x = tf.compat.v1.layers.Conv2D(filters=512,
                                       kernel_size=(7, 1),
                                       activation=tf.nn.relu)(x)
        x = tf.keras.layers.GlobalMaxPooling2D()(x)

        x = tf.compat.v1.layers.Dropout(rate=0.5)(
            x, training=mode == tf.estimator.ModeKeys.TRAIN)
        x = tf.compat.v1.layers.Dense(256, activation=tf.nn.relu)(x)

        embedding = tf.compat.v1.layers.Dense(embedding_dim, activation=None)(x)

    return embedding
