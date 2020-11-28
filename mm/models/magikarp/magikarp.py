import sys
import os


# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import models.shared.audio as audio
import models.shared.augmentation as augmentation
import argparse
from enum import Enum

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

AUDIO_SHAPE = None


class Mode(Enum):
    train_eval = "train_eval"
    export = "export"


def create_input_fn(mode: tf.estimator.ModeKeys,
                    input_prefix: str,
                    parallel_reads: int = 5,
                    batch_size: int = 32,
                    sample_rate=8000):
    feature_description = {
        'label': tf.io.FixedLenFeature([], tf.int64),
        'audio': tf.io.FixedLenFeature([AUDIO_SHAPE], tf.int64),
    }

    def decode_example(x):
        return tf.io.parse_single_example(x, feature_description)

    def cast_to_int16(x):
        x["audio"] = tf.cast(x["audio"], tf.int16)
        return x

    def input_fn():
        entries = input_prefix.split("/")
        path = "/".join(entries[:-1])
        prefix = entries[-1]

        files = [str(file) for file in pathlib.Path(path).glob(f"{prefix}")]

        dataset = tf.data.TFRecordDataset(filenames=files,
                                          num_parallel_reads=parallel_reads)
        dataset = dataset.map(decode_example)
        dataset = dataset.map(cast_to_int16)
        dataset = dataset.cache()

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.shuffle(buffer_size=100)
            dataset = dataset.map(augmentation.randomly_apply_augmentations(sample_rate=sample_rate))

        # Apply augmentation if is train

        dataset = dataset.batch(batch_size=batch_size)

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.repeat()

        return dataset

    return input_fn


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


def mfcc_model(x: tf.Tensor, num_labels: int,
               mode: tf.estimator.ModeKeys,
               regularization: float = 1e-6) -> tf.Tensor:

    x = tf.expand_dims(x, -1)

    print("X", x.shape)
    x = tf.compat.v1.layers.Conv2D(
        filters=64,
        kernel_size=(5, 2),
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    print("X", x.shape)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 2), strides=(1, 1))(x)
    print("X", x.shape)
    x = tf.compat.v1.layers.Conv2D(
        filters=64,
        kernel_size=(1, 5),
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    print("X", x.shape)
    x = tf.compat.v1.layers.MaxPooling2D(pool_size=(1, 2), strides=(1, 1))(x)
    # print("X", x.shape)
    # x = tf.compat.v1.layers.Conv2D(
        # filters=256,
        # kernel_size=(1, 2),
        # padding="valid",
        # activation=tf.nn.relu,
        # kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    print("X", x.shape)
    x = tf.compat.v1.layers.Conv2D(
        filters=256,
        kernel_size=(7, 1),
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    print("X", x.shape)
    x = tf.keras.layers.GlobalMaxPooling2D()(x)
    print("X", x.shape)

    x = tf.compat.v1.layers.Dropout(rate=0.50)(
        x, training=mode == tf.estimator.ModeKeys.TRAIN)
    print("X", x.shape)
    x = tf.compat.v1.layers.Dense(
        128,
        activation=tf.nn.relu,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    print("X", x.shape)
    logits = tf.compat.v1.layers.Dense(
        num_labels,
        activation=None,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(regularization))(x)
    return logits


def get_metric_ops(labels: tf.Tensor, predicted_class: tf.Tensor,
                   num_labels: int):
    metric_ops = {}

    def weights_label(label: int):
        return tf.cast(tf.equal(labels, label), tf.float32)

    for label in range(num_labels):
        metric_ops[f"{label}_accuracy"] = tf.metrics.accuracy(
            labels=labels,
            predictions=predicted_class,
            weights=weights_label(label))
        bools_label = tf.equal(labels, label)
        bools_pred = tf.equal(predicted_class, label)

        metric_ops[f"{label}_recall"] = tf.metrics.recall(
            labels=bools_label,
            predictions=bools_pred,
            weights=weights_label(label))
        metric_ops[f"{label}_precision"] = tf.metrics.precision(
            labels=bools_label,
            predictions=bools_pred,
            weights=weights_label(label))

    metric_ops["global_accuracy"] = tf.metrics.accuracy(
        labels=labels, predictions=predicted_class)
    return metric_ops


def make_model_fn(summary_output_dir: str,
                  num_labels: int,
                  sample_rate: int = 44100,
                  save_summaries_every: int = 100,
                  learning_rate: float = 0.001,
                  decay_rate: float = 0.95,
                  decay_steps: int = 50):
    def model_fn(features, labels, mode, config, params):
        audio_signal = features["audio"]

        # Expand single prediction to batch
        if mode == tf.estimator.ModeKeys.PREDICT:
            audio_signal = tf.expand_dims(audio_signal, 0)

        # Normalize audio to [-1, 1]
        signal = audio.normalize(audio_signal)

        if mode != tf.estimator.ModeKeys.PREDICT:
            tf.summary.audio(name="audio",
                             tensor=signal,
                             sample_rate=sample_rate)

        signal = audio.mfcc_feature(signal=signal,
                                    coefficients=13,
                                    sample_rate=sample_rate,
                                    frame_length=512,
                                    frame_step=256,
                                    fft_length=512,
                                    num_mel_bins=40,
                                    lower_edge_hertz=128,
                                    upper_edge_hertz=4000)

        # logits = raw_audio_model(signal=signal, num_labels=num_labels, mode=mode)

        logits = mfcc_model(x=signal, num_labels=num_labels, mode=mode)
        predict_op = tf.nn.softmax(logits)

        loss_op, train_op, train_logging_hooks, eval_metric_ops = None, None, None, None
        if mode != tf.estimator.ModeKeys.PREDICT:
            labels = features["label"]

            loss_op = tf.identity(tf.losses.sparse_softmax_cross_entropy(
                labels=labels, logits=logits),
                                  name="loss_op")

            exp_learning_rate = tf.compat.v1.train.exponential_decay(
                learning_rate=learning_rate,
                global_step=tf.compat.v1.train.get_global_step(),
                decay_steps=decay_steps,
                decay_rate=decay_rate,
                staircase=True)

            # Add to summary
            tf.summary.scalar("learning_rate", exp_learning_rate)

            # Add regularization
            reg_loss = tf.compat.v1.losses.get_regularization_loss()
            tf.summary.scalar("regularization_loss", reg_loss)

            total_loss = reg_loss + loss_op
            tf.summary.scalar("total_loss", total_loss)

            train_op = tf.compat.v1.train.AdamOptimizer(
                learning_rate=exp_learning_rate).minimize(
                    loss=total_loss,
                    global_step=tf.compat.v1.train.get_global_step())

            train_logging_hooks = [
                tf.estimator.LoggingTensorHook({"loss": "loss_op"},
                                               every_n_iter=20),
                tf.estimator.SummarySaverHook(
                    save_steps=save_summaries_every,
                    output_dir=summary_output_dir,
                    summary_op=tf.compat.v1.summary.merge_all())
            ]

            predicted_class = tf.argmax(predict_op, axis=-1)

            eval_metric_ops = get_metric_ops(labels=labels,
                                             predicted_class=predicted_class,
                                             num_labels=num_labels)

        # Squeeze prediction to vector again
        if mode == tf.estimator.ModeKeys.PREDICT:
            predict_op = tf.squeeze(predict_op, name="output")

        return tf.estimator.EstimatorSpec(mode=mode,
                                          predictions=predict_op,
                                          loss=loss_op,
                                          train_op=train_op,
                                          training_hooks=train_logging_hooks,
                                          eval_metric_ops=eval_metric_ops)

    return model_fn


def main():
    global AUDIO_SHAPE

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        required=True,
                        choices=[str(x).split(".")[1] for x in Mode],
                        help="one of (train_eval or export)")
    parser.add_argument(
        "--model_directory",
        required=True,
        help="Model directory -- where events & checkpoints is stored")
    parser.add_argument(
        "--train_prefix",
        help="absolute path to prefix of train files",
        type=str,
    )
    parser.add_argument(
        "--eval_prefix",
        help="absolute path to prefix of eval files",
        type=str,
    )
    parser.add_argument("--num_labels",
                        required=True,
                        type=int,
                        help="Number of labels in label_map")
    parser.add_argument("--clip_length",
                        default=1.0,
                        type=float,
                        help="Clip length in seconds of the audio")
    parser.add_argument("--sample_rate",
                        default=8000,
                        type=int,
                        help="Sample rate of the audio")
    parser.add_argument("--batch_size",
                        default=32,
                        type=int,
                        help="Batch size of training")
    parser.add_argument("--start_learning_rate",
                        default=0.001,
                        type=float,
                        help="Start learning rate")
    parser.add_argument("--learning_rate_decay",
                        default=0.95,
                        type=float,
                        help="Decay of learning rate")
    parser.add_argument("--learning_decay_steps",
                        default=50,
                        type=int,
                        help="Decay every decay_steps")
    parser.add_argument("--save_summary_every",
                        default=10000,
                        type=int,
                        help="Same summary every n steps")
    parser.add_argument("--eval_every",
                        default=10000,
                        type=int,
                        help="Evaluates on full dataset n steps")
    parser.add_argument("--max_steps",
                        default=10000000,
                        type=int,
                        help="Evaluates on full dataset n steps")
    parser.add_argument("--parallel_reads",
                        default=5,
                        type=int,
                        help="Parallel reads of dataset")

    args = parser.parse_args()

    AUDIO_SHAPE = int(args.clip_length * args.sample_rate)

    config = tf.estimator.RunConfig(
        model_dir=args.model_directory,
        save_summary_steps=args.save_summary_every,
        log_step_count_steps=100,
        save_checkpoints_steps=args.eval_every,
    )

    estimator = tf.estimator.Estimator(model_fn=make_model_fn(
        summary_output_dir=args.model_directory,
        num_labels=args.num_labels,
        sample_rate=args.sample_rate,
        save_summaries_every=args.save_summary_every,
        learning_rate=args.start_learning_rate,
        decay_rate=args.learning_rate_decay,
        decay_steps=args.learning_decay_steps),
                                       model_dir=args.model_directory,
                                       config=config)

    if args.mode == Mode.train_eval.value:
        train_spec = tf.estimator.TrainSpec(
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.TRAIN,
                                     input_prefix=args.train_prefix,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size,
                                     sample_rate=args.sample_rate),
            max_steps=args.max_steps,
        )

        eval_spec = tf.estimator.EvalSpec(
            steps=args.eval_every,
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.EVAL,
                                     input_prefix=args.eval_prefix,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size,
                                     sample_rate=args.sample_rate),
            throttle_secs=5,
        )

        tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)

    elif args.mode == Mode.export.value:

        def serving_input_receiver_fn():
            inputs = {
                "audio":
                tf.compat.v1.placeholder(dtype=tf.int16,
                                         shape=[AUDIO_SHAPE],
                                         name="input")
            }
            return tf.estimator.export.ServingInputReceiver(
                features=inputs, receiver_tensors=inputs)

        estimator.export_saved_model(
            export_dir_base=args.model_directory,
            serving_input_receiver_fn=serving_input_receiver_fn)
    else:
        raise NotImplementedError(f"Unknown mode {args.mode}")


if __name__ == "__main__":
    main()
