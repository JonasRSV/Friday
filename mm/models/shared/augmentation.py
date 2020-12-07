import tensorflow as tf


def randomly_apply_augmentations(sample_rate: int):
    def inject_noise(audio: tf.Tensor, level: int) -> tf.Tensor:
        return audio + tf.cast(tf.random.normal(shape=audio.shape, mean=0, stddev=level), tf.int16)

    def shift(audio: tf.Tensor, amount: int) -> tf.Tensor:
        return tf.roll(audio, shift=amount, axis=0)

    def mapping(example: tf.train.Example):
        random_number = tf.random.uniform(minval=0, maxval=1, shape=())

        example["audio"] = tf.case(
            [
                (tf.greater(0.1, random_number), lambda: inject_noise(example["audio"], level=10)),
                (tf.greater(0.2, random_number), lambda: inject_noise(example["audio"], level=50)),
                (tf.greater(0.3, random_number), lambda: inject_noise(example["audio"], level=100)),
                (tf.greater(0.4, random_number), lambda: inject_noise(example["audio"], level=200)),
                (tf.greater(0.5, random_number), lambda: shift(example["audio"], amount=200)),
                (tf.greater(0.6, random_number), lambda: shift(example["audio"], amount=-50)),
                (tf.greater(0.7, random_number), lambda: shift(inject_noise(example["audio"], level=200), 200)),
                (tf.greater(0.8, random_number), lambda: shift(inject_noise(example["audio"], level=150), 150)),
                (tf.greater(0.9, random_number), lambda: shift(inject_noise(example["audio"], level=130), 70)),
            ],
            default=lambda: example["audio"])

        return example

    return mapping


