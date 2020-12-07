import tensorflow as tf


def spectrogram_model_tiny(x: tf.Tensor,
                    num_labels: int,
                    mode: tf.estimator.ModeKeys,
                    regularization: float = 1e-6) -> tf.Tensor:
    x = tf.expand_dims(x, -1)

    x = tf.compat.v1.layers.Conv2D(
        filters=64,
        kernel_size=(5, 2),
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 2), strides=(1, 1))(x)
    x = tf.compat.v1.layers.Conv2D(
        filters=64,
        kernel_size=(1, 5),
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 2), strides=(1, 1))(x)
    x = tf.compat.v1.layers.Conv2D(
        filters=256,
        kernel_size=(1, 2),
        padding="valid",
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    x = tf.compat.v1.layers.Conv2D(
        filters=256,
        kernel_size=(7, 1),
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    x = tf.keras.layers.GlobalMaxPooling2D()(x)

    x = tf.compat.v1.layers.Dropout(rate=0.50)(
        x, training=mode == tf.estimator.ModeKeys.TRAIN)
    x = tf.compat.v1.layers.Dense(
        128,
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    x = tf.compat.v1.layers.Dense(
        128,
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    logits = tf.compat.v1.layers.Dense(
        num_labels,
        activation=None,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    return logits
