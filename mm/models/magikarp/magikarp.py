import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import tensorflow_probability as tfp
import models.shared.audio as audio
import models.shared.augmentation as augmentation
import argparse
import models.magikarp.architechtures as arch
from enum import Enum

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)

AUDIO_SHAPE = None


class Mode(Enum):
    train_eval = "train_eval"
    export = "export"


def create_input_fn(mode: tf.estimator.ModeKeys,
                    num_labels: int,
                    input_prefix: str,
                    parallel_reads: int = 5,
                    batch_size: int = 32,
                    sample_rate=8000,
                    use_mixup: bool = True):
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

        # Apply augmentation if is train
        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.shuffle(buffer_size=100)
            dataset = dataset.map(
                augmentation.randomly_apply_augmentations(
                    sample_rate=sample_rate))

        dataset = dataset.batch(batch_size=batch_size)

        # https://arxiv.org/pdf/1710.09412.pdf
        if use_mixup:
            distribution = tfp.distributions.Beta(2.0, 2.0)

            def apply_mixup(record: dict):
                dyn_batch_size = tf.shape(record["label"])[0]

                weights = tf.reshape(distribution.sample(dyn_batch_size), [dyn_batch_size, 1])
                indexes = tf.random.shuffle(tf.range(0, dyn_batch_size))
                record["audio"] = audio.normalize_audio(record["audio"])

                print("audio", record["audio"], "indexes", indexes)

                x1, x2 = record["audio"], tf.gather(record["audio"], indexes)
                y1, y2 = tf.one_hot(record["label"],
                                    depth=num_labels), tf.one_hot(tf.gather(record["label"], indexes),
                                                                  depth=num_labels)

                x = x1 * weights + x2 * (1 - weights)
                y = y1 * weights + y2 * (1 - weights)

                record["audio"] = x
                record["soft-label"] = y

                return record

            dataset = dataset.map(apply_mixup)

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.repeat()

        return dataset

    return input_fn


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
                  sample_rate: int = 8000,
                  save_summaries_every: int = 100,
                  learning_rate: float = 0.001,
                  use_mixup: bool = False):
    def model_fn(features, labels, mode, config, params):
        audio_signal = features["audio"]

        # Expand single prediction to batch
        if mode == tf.estimator.ModeKeys.PREDICT:
            audio_signal = tf.expand_dims(audio_signal, 0)

        # Normalize audio to [-1, 1]
        if (mode == tf.estimator.ModeKeys.TRAIN) and use_mixup:
            # IF we are using mixup and training, the input audio has already been normalize
            signal = audio_signal
        else:
            signal = audio.normalize_audio(audio_signal)

        if mode != tf.estimator.ModeKeys.PREDICT:
            tf.summary.audio(name="audio",
                             tensor=signal,
                             sample_rate=sample_rate)

        signal = audio.mfcc_feature(signal=signal,
                                    coefficients=27,
                                    sample_rate=sample_rate,
                                    frame_length=512,
                                    frame_step=256,
                                    fft_length=512,
                                    num_mel_bins=128,
                                    lower_edge_hertz=128,
                                    upper_edge_hertz=4000)

        # logits = raw_audio_model(signal=signal, num_labels=num_labels, mode=mode)

        logits = arch.spectrogram_model_tiny(x=signal, num_labels=num_labels, mode=mode)
        predict_op = tf.nn.softmax(logits)

        loss_op, train_op, train_logging_hooks, eval_metric_ops = None, None, None, None
        if mode != tf.estimator.ModeKeys.PREDICT:
            # If we are using mixup optimize towards mixup labels instead
            if (mode == tf.estimator.ModeKeys.TRAIN) and use_mixup:
                loss_op = tf.identity(tf.losses.softmax_cross_entropy(
                    onehot_labels=features["soft-label"], logits=logits),
                    name="loss_op")
            else:
                loss_op = tf.identity(tf.losses.sparse_softmax_cross_entropy(
                    labels=features["label"], logits=logits),
                    name="loss_op")

            decay_learning_rate = tf.compat.v1.train.cosine_decay_restarts(
                learning_rate=learning_rate,
                global_step=tf.compat.v1.train.get_global_step(),
                first_decay_steps=1000,
                t_mul=2.0,
                m_mul=1.0,
                alpha=0.0)

            # Add to summary
            tf.summary.scalar("learning_rate", decay_learning_rate)

            # Add regularization
            reg_loss = tf.compat.v1.losses.get_regularization_loss()
            tf.summary.scalar("regularization_loss", reg_loss)

            total_loss = reg_loss + loss_op
            tf.summary.scalar("total_loss", total_loss)

            train_op = tf.compat.v1.train.AdamOptimizer(
                learning_rate=decay_learning_rate).minimize(
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

            if mode == tf.estimator.ModeKeys.EVAL:
                eval_metric_ops = get_metric_ops(labels=features["label"],
                                                 predicted_class=tf.argmax(predict_op, axis=-1),
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
                        default=2.0,
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

    # https://arxiv.org/pdf/1710.09412.pdf
    parser.add_argument("--use_mixup",
                        type=bool,
                        default=False,
                        help="Use mixup in training")

    args = parser.parse_args()

    AUDIO_SHAPE = int(args.clip_length * args.sample_rate)

    config = tf.estimator.RunConfig(
        model_dir=args.model_directory,
        save_summary_steps=args.save_summary_every,
        log_step_count_steps=100,
        save_checkpoints_steps=args.eval_every,
    )

    estimator = tf.estimator.Estimator(
        model_fn=make_model_fn(
            summary_output_dir=args.model_directory,
            num_labels=args.num_labels,
            sample_rate=args.sample_rate,
            save_summaries_every=args.save_summary_every,
            learning_rate=args.start_learning_rate,
            use_mixup=args.use_mixup),
        model_dir=args.model_directory,
        config=config)

    if args.mode == Mode.train_eval.value:
        train_spec = tf.estimator.TrainSpec(
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.TRAIN,
                                     num_labels=args.num_labels,
                                     input_prefix=args.train_prefix,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size,
                                     sample_rate=args.sample_rate,
                                     use_mixup=args.use_mixup),
            max_steps=args.max_steps,
        )

        eval_spec = tf.estimator.EvalSpec(
            steps=args.eval_every,
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.EVAL,
                                     num_labels=args.num_labels,
                                     input_prefix=args.eval_prefix,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size,
                                     sample_rate=args.sample_rate,
                                     use_mixup=False),
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
