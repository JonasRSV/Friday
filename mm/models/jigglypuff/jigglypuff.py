import sys
import os

# Some systems don't use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import models.shared.audio as audio
import argparse
import models.jigglypuff.architechtures as arch
from enum import Enum

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)


class Mode(Enum):
    train_eval = "train_eval"
    export = "export"


def create_input_fn(mode: tf.estimator.ModeKeys,
                    input_prefix: str,
                    parallel_reads: int = 5,
                    batch_size: int = 32,
                    sample_rate=8000):
    feature_description = {
        'label': tf.io.VarLenFeature(tf.int64),
        'audio': tf.io.VarLenFeature(tf.int64),
    }

    def decode_example(x: tf.train.Example) -> tf.train.Example:
        return tf.io.parse_single_example(x, feature_description)

    def cast_to_int16(x: tf.train.Example) -> tf.train.Example:
        x["audio"] = tf.cast(x["audio"], tf.int16)
        return x

    def add_lengths(x: tf.train.Example) -> tf.train.Example:
        x["label_length"] = tf.squeeze(x["label"].dense_shape)
        x["audio_length"] = tf.squeeze(x["audio"].dense_shape)
        return x

    def add_logit_length_factor(x: dict) -> dict:
        """Factor to multiply length of padded logits with to get length of unpadded logits."""
        x["logit_length_factor"] = tf.cast(x["audio_length"], tf.float32) / tf.cast(tf.shape(x["audio"])[1], tf.float32)
        return x

    def sparse_to_dense(x: dict) -> tf.train.Example:
        x["audio"] = tf.sparse.to_dense(x["audio"], default_value=0)
        x["label"] = tf.sparse.to_dense(x["label"], default_value=0)
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
        dataset = dataset.map(add_lengths)

        # Apply augmentation if is train
        # if mode == tf.estimator.ModeKeys.TRAIN:
        #    dataset = dataset.shuffle(buffer_size=100)

        dataset = dataset.batch(batch_size=batch_size)
        # Sparse to dense does padding
        dataset = dataset.map(sparse_to_dense)
        dataset = dataset.map(add_logit_length_factor)

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.repeat()

        return dataset

    return input_fn


def get_predict_ops(logits: tf.Tensor, logit_length: tf.Tensor, labels: tf.Tensor):
    top_beam_search, _ = tf.nn.ctc_beam_search_decoder_v2(logits,
                                                          logit_length,
                                                          beam_width=600)

    ctc_loss = tf.nn.ctc_loss_v2(labels=labels, logits=logits,
                                 label_length=tf.expand_dims(tf.shape(labels)[1], 0),
                                 logit_length=logit_length,
                                 blank_index=-1)

    predict_op = tf.squeeze(tf.sparse.to_dense(top_beam_search[0])[0])
    logits = tf.squeeze(logits)[:logit_length[0]]

    return predict_op, tf.shape(predict_op), logits, tf.shape(logits), -tf.squeeze(ctc_loss)


def get_metric_ops(labels: tf.Tensor,
                   logits: tf.Tensor,
                   label_length: tf.Tensor,
                   logit_length: tf.Tensor,
                   num_phonemes: int):
    metric_ops = {}
    ctc_loss = tf.nn.ctc_loss_v2(labels=labels, logits=logits,
                                 label_length=label_length,
                                 logit_length=logit_length,
                                 blank_index=-1)

    metric_ops["ctc_loss"] = tf.metrics.mean(ctc_loss)
    return tf.reduce_mean(ctc_loss), metric_ops


def get_train_ops(features: dict,
                  logit_length: tf.Tensor,
                  logits: tf.Tensor,
                  learning_rate: float,
                  save_summaries_every: int,
                  summary_output_dir: str):
    ctc_loss = tf.nn.ctc_loss_v2(labels=features["label"], logits=logits,
                                 label_length=features["label_length"],
                                 logit_length=logit_length,
                                 blank_index=-1)

    loss_op = tf.reduce_mean(ctc_loss, name="loss_op")

    decay_learning_rate = tf.compat.v1.train.cosine_decay_restarts(
        learning_rate=learning_rate,
        global_step=tf.compat.v1.train.get_global_step(),
        first_decay_steps=10000,
        t_mul=1.0,
        m_mul=0.98,
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

    final_logits = tf.transpose(logits, (1, 0, 2))
    top_beam_search = tf.expand_dims(final_logits[0], 0)
    top_beam_search = tf.transpose(top_beam_search, (1, 0, 2))
    top_beam_search, _ = tf.nn.ctc_beam_search_decoder_v2(top_beam_search,
                                                          tf.cast(tf.expand_dims(logit_length[0], 0),
                                                                  dtype=tf.int32),
                                                          beam_width=300)
    top_beam_search = top_beam_search[0]
    top_beam_search = tf.sparse.to_dense(top_beam_search)
    tf.identity(top_beam_search, name="top_beam_search")
    tf.identity(features["label"][0], name="final_labels")

    train_logging_hooks = [
        tf.estimator.LoggingTensorHook({"loss": "loss_op",
                                        "final_labels": "final_labels",
                                        "top_beam_search": "top_beam_search",
                                        }, every_n_iter=50),
        tf.estimator.SummarySaverHook(
            save_steps=save_summaries_every,
            output_dir=summary_output_dir,
            summary_op=tf.compat.v1.summary.merge_all())
    ]

    return loss_op, train_op, train_logging_hooks


def make_model_fn(num_phonemes: int,
                  summary_output_dir: str,
                  sample_rate: int = 8000,
                  save_summaries_every: int = 100,
                  learning_rate: float = 0.001):
    def model_fn(features, labels, mode, config, params):
        audio_signal = features["audio"]

        # Expand single prediction to batch
        if mode == tf.estimator.ModeKeys.PREDICT:
            audio_signal = tf.expand_dims(audio_signal, 0)
            features["label"] = tf.expand_dims(features["label"], 0)
            features["logit_length_factor"] = tf.expand_dims(features["logit_length_factor"], 0)

        signal = audio.normalize_audio(audio_signal)

        signal = audio.mfcc_feature(signal=signal,
                                    coefficients=27,
                                    sample_rate=sample_rate,
                                    frame_length=512,
                                    frame_step=256,
                                    fft_length=512,
                                    num_mel_bins=120,
                                    lower_edge_hertz=1,
                                    upper_edge_hertz=4000)

        # logits = arch.spectrogram_model_big(signal, num_phonemes=num_phonemes, mode=mode)
        logits = arch.rnn(signal, num_phonemes=num_phonemes, mode=mode)

        # Make it time-major
        logits = tf.transpose(logits, (1, 0, 2))
        # Calculate length of un-padded logit sequence
        logit_length = features["logit_length_factor"] * tf.cast(tf.shape(logits)[0], tf.float32)
        logit_length = tf.cast(logit_length, tf.int32, name="logit_length")

        loss_op, train_op, train_logging_hooks, eval_metric_ops, predict_op = None, None, None, None, None
        if mode == tf.estimator.ModeKeys.TRAIN:
            loss_op, train_op, train_logging_hooks = get_train_ops(
                features=features,
                logit_length=logit_length,
                logits=logits,
                learning_rate=learning_rate,
                save_summaries_every=save_summaries_every,
                summary_output_dir=summary_output_dir)
        elif mode == tf.estimator.ModeKeys.EVAL:
            loss_op, eval_metric_ops = get_metric_ops(labels=features["label"],
                                                      logits=logits,
                                                      label_length=features["label_length"],
                                                      logit_length=logit_length,
                                                      num_phonemes=num_phonemes)
        elif mode == tf.estimator.ModeKeys.PREDICT:
            predict_op, predict_shape, logits_op, logits_shape, ctc_op = get_predict_ops(
                logits=logits,
                logit_length=logit_length,
                labels=features["label"]
            )

            tf.identity(predict_op, name="output")
            tf.identity(predict_shape, name="output_shape")
            tf.identity(logits_op, name="logits")
            tf.identity(logits_shape, name="logits_shape")
            tf.identity(ctc_op, name="log_prob")
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
    parser.add_argument("--num_phonemes",
                        required=True,
                        type=int,
                        help="Number of phonemes (including blank and special signs)")
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
            num_phonemes=args.num_phonemes,
            sample_rate=args.sample_rate,
            save_summaries_every=args.save_summary_every,
            learning_rate=args.start_learning_rate),
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
                                     input_prefix=args.train_prefix,
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
                                             shape=[None],
                                             name="input"),
                "label":
                    tf.compat.v1.placeholder(dtype=tf.int32,
                                             shape=[None],
                                             name="labels"),
                # We have no padding when serving.
                "logit_length_factor": tf.constant(1.0, dtype=tf.float32)
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
