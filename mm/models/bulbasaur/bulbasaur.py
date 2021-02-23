import sys
import os

# Some systems don't use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import models.shared.audio as audio
import argparse
import models.bulbasaur.architechtures as arch
from enum import Enum

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)


class Mode(Enum):
    train_eval = "train_eval"
    export = "export"


def create_input_fn(mode: tf.estimator.ModeKeys,
                    input_prefix: str,
                    audio_length: int,
                    parallel_reads: int = 5,
                    batch_size: int = 32):
    feature_description = {
        'label': tf.io.FixedLenFeature(tf.int64, [1]),
        'audio': tf.io.FixedLenFeature(tf.int64, [audio_length]),
    }

    def decode_example(x: tf.train.Example) -> tf.train.Example:
        return tf.io.parse_single_example(x, feature_description)

    def cast_to_int16(x: tf.train.Example) -> tf.train.Example:
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

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.shuffle(buffer_size=100)

        dataset = dataset.batch(batch_size=batch_size)
        # Sparse to dense does padding

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.repeat()

        return dataset

    return input_fn


def get_predict_ops(stored_embeddings: tf.Tensor,
                    signal: tf.Tensor,
                    sample_rate: int,
                    embedding_dim: int):
    similarities = tf.constant(1)
    predict_op = tf.constant(1)
    return predict_op, similarities


def get_metric_ops(left_embeddings: tf.Tensor,
                   right_embeddings: tf.Tensor,
                   labels: tf.Tensor):
    metric_ops = {}

    return metric_ops


def get_train_ops(left_embeddings: tf.Tensor,
                  right_embeddings: tf.Tensor,
                  labels: tf.Tensor,
                  learning_rate: float,
                  save_summaries_every: int,
                  summary_output_dir: str):
    loss_op = tf.constant(0)
    decay_learning_rate = tf.compat.v1.train.cosine_decay_restarts(
        learning_rate=learning_rate,
        global_step=tf.compat.v1.train.get_global_step(),
        first_decay_steps=1000,
        t_mul=2.0,
        m_mul=1.0,
        alpha=0.0,
        name="learning_rate")

    # Add to summary
    tf.summary.scalar("learning_rate", decay_learning_rate)

    # Add regularization
    reg_loss = tf.compat.v1.losses.get_regularization_loss()
    tf.summary.scalar("regularization_loss", reg_loss)

    total_loss = loss_op + reg_loss
    tf.summary.scalar("total_loss", total_loss)

    train_op = tf.compat.v1.train.AdamOptimizer(
        learning_rate=decay_learning_rate).minimize(
        loss=total_loss,
        global_step=tf.compat.v1.train.get_global_step())

    train_logging_hooks = [
        tf.estimator.LoggingTensorHook(
            {"loss": "loss_op"},
            every_n_iter=50),
        tf.estimator.SummarySaverHook(
            save_steps=save_summaries_every,
            output_dir=summary_output_dir,
            summary_op=tf.compat.v1.summary.merge_all())
    ]

    return loss_op, train_op, train_logging_hooks


def extract_mfcc(signal: tf.Tensor, sample_rate: int):
    return audio.mfcc_feature(signal=signal,
                              coefficients=27,
                              sample_rate=sample_rate,
                              frame_length=512,
                              frame_step=256,
                              fft_length=512,
                              num_mel_bins=120,
                              lower_edge_hertz=1,
                              upper_edge_hertz=4000)


def get_embedding(audio_signal: tf.Tensor, sample_rate: int, embedding_dim: int, mode: tf.estimator.ModeKeys):
    signal = extract_mfcc(signal=audio.normalize_audio(audio_signal), sample_rate=sample_rate)
    return arch.kaggle_cnn(signal, embedding_dim=embedding_dim, mode=mode)


def make_model_fn(embedding_dim: int,
                  summary_output_dir: str,
                  sample_rate: int = 8000,
                  save_summaries_every: int = 100,
                  learning_rate: float = 0.001):
    def model_fn(features, labels, mode, config, params):
        loss_op, train_op, train_logging_hooks, eval_metric_ops, predict_op = None, None, None, None, None
        if mode == tf.estimator.ModeKeys.TRAIN:
            left_embeddings = get_embedding(features["left_audio"],
                                            sample_rate=sample_rate,
                                            embedding_dim=embedding_dim,
                                            mode=mode)
            right_embeddings = get_embedding(features["right_audio"],
                                             sample_rate=sample_rate,
                                             embedding_dim=embedding_dim,
                                             mode=mode)

            loss_op, train_op, train_logging_hooks = get_train_ops(
                left_embeddings=left_embeddings,
                right_embeddings=right_embeddings,
                labels=features["label"],
                learning_rate=learning_rate,
                save_summaries_every=save_summaries_every,
                summary_output_dir=summary_output_dir)
        elif mode == tf.estimator.ModeKeys.EVAL:
            left_embeddings = get_embedding(features["left_audio"],
                                            sample_rate=sample_rate,
                                            embedding_dim=embedding_dim,
                                            mode=mode)
            right_embeddings = get_embedding(features["right_audio"],
                                             sample_rate=sample_rate,
                                             embedding_dim=embedding_dim,
                                             mode=mode)

            loss_op, eval_metric_ops = get_metric_ops(left_embeddings=left_embeddings,
                                                      right_embeddings=right_embeddings,
                                                      labels=features["label"])
        elif mode == tf.estimator.ModeKeys.PREDICT:
            predict_op, similarities_op = get_predict_ops(
                stored_embeddings=features["embeddings"],
                signal=features["audio"],
                sample_rate=sample_rate,
                embedding_dim=embedding_dim
            )

            tf.identity(predict_op, name="output")
            tf.identity(tf.shape(predict_op), name="output_shape")
        else:
            raise Exception(f"Unknown ModeKey {mode}")

        return tf.estimator.EstimatorSpec(mode=mode,
                                          predictions=predict_op,
                                          loss=loss_op,
                                          train_op=train_op,
                                          training_hooks=train_logging_hooks,
                                          eval_metric_ops=eval_metric_ops)

    return model_fn


def main():
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
    parser.add_argument("--embedding_dim",
                        required=True,
                        type=int,
                        help="Dimension of embeddings")
    parser.add_argument("--clip_length",
                        required=True,
                        type=float,
                        help="Length of audio in seconds")
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

    args = parser.parse_args()

    config = tf.estimator.RunConfig(
        model_dir=args.model_directory,
        save_summary_steps=args.save_summary_every,
        log_step_count_steps=10,
        save_checkpoints_steps=args.eval_every,
    )

    estimator = tf.estimator.Estimator(
        model_fn=make_model_fn(
            summary_output_dir=args.model_directory,
            embedding_dim=args.embedding_dim,
            sample_rate=args.sample_rate,
            save_summaries_every=args.save_summary_every,
            learning_rate=args.start_learning_rate),
        model_dir=args.model_directory,
        config=config)

    if args.mode == Mode.train_eval.value:
        train_spec = tf.estimator.TrainSpec(
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.TRAIN,
                                     input_prefix=args.train_prefix,
                                     audio_length=int(args.clip_length * args.sample_rate),
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size),
            max_steps=args.max_steps,
        )

        eval_spec = tf.estimator.EvalSpec(
            steps=args.eval_every,
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.EVAL,
                                     input_prefix=args.train_prefix,
                                     audio_length=int(args.clip_length * args.sample_rate),
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size),
            throttle_secs=5,
        )

        tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)

    elif args.mode == Mode.export.value:

        def serving_input_receiver_fn():
            inputs = {}
            return tf.estimator.export.ServingInputReceiver(
                features=inputs, receiver_tensors=inputs)

        estimator.export_saved_model(
            export_dir_base=args.model_directory,
            serving_input_receiver_fn=serving_input_receiver_fn)
    else:
        raise NotImplementedError(f"Unknown mode {args.mode}")


if __name__ == "__main__":
    main()
