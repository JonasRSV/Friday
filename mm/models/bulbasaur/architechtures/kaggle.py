import tensorflow as tf


# Taken from https://www.kaggle.com/c/tensorflow-speech-recognition-challenge/discussion/47715
def kaggle_cnn(x: tf.Tensor,
               embedding_dim: int,
               mode: tf.estimator.ModeKeys,
               regularization: float = 1e-6) -> tf.Tensor:
    with tf.variable_scope('kaggle_cnn', reuse=tf.AUTO_REUSE):
        x = tf.expand_dims(x, -1)
        print("x", x)
        x = tf.compat.v1.layers.Conv2D(filters=128,
                                       kernel_size=(6, 6),
                                       strides=(2, 2),
                                       activation=tf.nn.relu,
                                       name="kaggle_cnn_1_c")(x)

        # x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 3), strides=(1, 3),
                                             # name="kaggle_cnn_1_m")(x)
        # x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 3), strides=(1, 1), name="kaggle_cnn_1_m")(x)
        print("x", x)
        x = tf.compat.v1.layers.Conv2D(filters=128,
                                       kernel_size=(1, 7),
                                       activation=tf.nn.relu,
                                       name="kaggle_cnn_2_c")(x)
        print("x", x)
        x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 4), strides=(1, 1),
                                             name="kaggle_cnn_2_m")(x)
        print("x", x)
        x = tf.compat.v1.layers.Conv2D(filters=256,
                                       kernel_size=(1, 9),
                                       padding="valid",
                                       activation=tf.nn.relu,
                                       name="kaggle_cnn_3_c")(x)
        print("x", x)
        x = tf.compat.v1.layers.Conv2D(filters=512,
                                       kernel_size=(7, 1),
                                       strides=(1, 1),
                                       activation=tf.nn.relu,
                                       name="kaggle_cnn_4_c")(x)
        print("x", x)
        x = tf.keras.layers.GlobalMaxPooling2D(name="kaggle_cnn_mp")(x)
        print("x", x)

        #x = tf.compat.v1.layers.Dropout(rate=0.1, name="kaggle_cnn_dropout")(
        #    x, training=mode == tf.estimator.ModeKeys.TRAIN,
        #    )
        #print("x", x)
        x = tf.compat.v1.layers.Dense(512, activation=tf.nn.relu, name="kaggle_cnn_1d")(x)
        print("x", x)

        embedding = tf.compat.v1.layers.Dense(embedding_dim, activation=None, name="kaggle_cnn_2d")(x)
        print("x", x)

    return embedding
