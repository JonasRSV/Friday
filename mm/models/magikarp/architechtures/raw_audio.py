import tensorflow as tf


def raw_audio_model(signal: tf.Tensor, num_labels: int,
                    mode: tf.estimator.ModeKeys) -> tf.Tensor:
    """A convolution based model.

    Args:
        signal: Audio signal scaled to [-1, 1]
        num_labels: The number of logits the model is expected to return
        mode: The mode the model is running in (TRAINING or PREDICT)
    Returns:
        Logits
    """

    x = tf.expand_dims(signal, -1)
    x = tf.compat.v1.layers.Conv1D(filters=2,
                                   kernel_size=500,
                                   strides=20,
                                   activation=tf.nn.relu)(x)
    x = tf.compat.v1.layers.Conv1D(filters=5,
                                   kernel_size=200,
                                   strides=4,
                                   activation=tf.nn.relu)(x)
    x = tf.compat.v1.layers.MaxPooling1D(15, strides=10)(x)
    x = tf.compat.v1.layers.Flatten()(x)
    x = tf.compat.v1.layers.Dropout(rate=0.25)(
        x, training=mode == tf.estimator.ModeKeys.TRAIN)
    x = tf.compat.v1.layers.Dense(64, activation=tf.nn.relu)(x)
    x = tf.compat.v1.layers.Dense(num_labels, activation=None)(x)

    return x
