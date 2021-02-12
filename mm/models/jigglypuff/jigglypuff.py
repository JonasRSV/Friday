import sys
import os

# Some systems dont use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import models.shared.audio as audio
import models.shared.augmentation as augmentation
import argparse
import numpy as np
import models.jigglypuff.architechtures as arch
from enum import Enum

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)


class Mode(Enum):
    train_eval = "train_eval"
    export = "export"


def create_input_fn(max_label_sequence_length: int,
                    max_audio_sequence_length: int,
                    mode: tf.estimator.ModeKeys,
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

    def sparse_to_dense(x: tf.train.Example) -> tf.train.Example:
        x["audio"] = tf.sparse.to_dense(x["audio"])
        x["label"] = tf.sparse.to_dense(x["label"])
        return x

    def pad_phoneme_sequence_numpy(x: np.ndarray) -> np.ndarray:
        return np.append(x, np.zeros(max_label_sequence_length - x.size, dtype=x.dtype))

    def pad_audio_sequence_numpy(x: np.ndarray) -> np.ndarray:
        return np.append(x, np.zeros(max_audio_sequence_length - x.size, dtype=x.dtype))

    def pad_sequences(x: tf.train.Example) -> tf.train.Example:
        x["label"] = tf.compat.v1.numpy_function(pad_phoneme_sequence_numpy, inp=[x["label"]], Tout=tf.int64)
        x["audio"] = tf.compat.v1.numpy_function(pad_audio_sequence_numpy, inp=[x["audio"]], Tout=tf.int16)

        x["label"] = tf.reshape(x["label"], [max_label_sequence_length])
        x["audio"] = tf.reshape(x["audio"], [max_audio_sequence_length])
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
        dataset = dataset.map(sparse_to_dense)
        dataset = dataset.map(pad_sequences)
        dataset = dataset.cache()

        # Apply augmentation if is train
        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.shuffle(buffer_size=100)

        dataset = dataset.batch(batch_size=batch_size)

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.repeat()

        return dataset

    return input_fn


def get_metric_ops(labels: tf.Tensor, predicted_class: tf.Tensor, num_phonemes: int):
    metric_ops = {}

    return metric_ops


def make_model_fn(num_phonemes: int,
                  summary_output_dir: str,
                  sample_rate: int = 8000,
                  save_summaries_every: int = 100,
                  learning_rate: float = 0.001):
    def model_fn(features, labels, mode, config, params):

        print("Features", features, "audio", features["audio"].shape, "label", features["label"].shape)
        # features["audio"] = tf.reshape(features["audio"], [-1, 16000])
        print("Features", features, "audio", features["audio"].shape, "label", features["label"].shape)

        audio_signal = features["audio"]

        # Expand single prediction to batch
        if mode == tf.estimator.ModeKeys.PREDICT:
            audio_signal = tf.expand_dims(audio_signal, 0)

        signal = audio.normalize_audio(audio_signal)

        if mode != tf.estimator.ModeKeys.PREDICT:
            tf.summary.audio(name="audio",
                             tensor=signal,
                             sample_rate=sample_rate)

        signal = audio.mfcc_feature(signal=signal,
                                    coefficients=120,
                                    sample_rate=sample_rate,
                                    frame_length=512,
                                    frame_step=256,
                                    fft_length=512,
                                    num_mel_bins=128,
                                    lower_edge_hertz=128,
                                    upper_edge_hertz=4000)

        logits = arch.spectrogram_model_big(signal, num_phonemes=num_phonemes, mode=mode)
        predict_op = tf.nn.softmax(logits)

        # If 'padded_audio_length' became 'frames' long, then
        # audio_length would become approximately (frames * audio_length/padded_audio_length) frames long.

        logit_frames = tf.cast(logits.shape[1] * features["audio_length"] / features["audio"].shape[-1],
                               tf.int32,
                               name="logit_frames")

        print("logits", logits, "predictions", predict_op, "frames", logit_frames)

        loss_op, train_op, train_logging_hooks, eval_metric_ops = None, None, None, None
        if mode != tf.estimator.ModeKeys.PREDICT:
            ctc_loss = tf.nn.ctc_loss_v2(labels=features["label"], logits=logits,
                                         label_length=features["label_length"],
                                         logit_length=logit_frames,
                                         logits_time_major=False,
                                         blank_index=0)

            loss_op = tf.reduce_mean(ctc_loss / tf.cast(logit_frames, ctc_loss.dtype),
                                     name="loss_op")

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

            total_loss = reg_loss + loss_op
            tf.summary.scalar("total_loss", total_loss)

            train_op = tf.compat.v1.train.AdamOptimizer(
                learning_rate=decay_learning_rate).minimize(
                loss=total_loss,
                global_step=tf.compat.v1.train.get_global_step())

            train_logging_hooks = [
                tf.estimator.LoggingTensorHook({"loss": "loss_op",
                                                "logit_frames": "logit_frames",
                                                "learning_rate": "learning_rate"
                                                }, every_n_iter=1),
                tf.estimator.SummarySaverHook(
                    save_steps=save_summaries_every,
                    output_dir=summary_output_dir,
                    summary_op=tf.compat.v1.summary.merge_all())
            ]

            if mode == tf.estimator.ModeKeys.EVAL:
                eval_metric_ops = get_metric_ops(labels=features["label"],
                                                 predicted_class=tf.argmax(predict_op, axis=-1),
                                                 num_phonemes=num_phonemes)

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
    parser.add_argument("--max_label_sequence_length",
                        required=True,
                        type=int,
                        help="Length of longest label sequence")
    parser.add_argument("--max_audio_sequence_length",
                        required=True,
                        type=int,
                        help="Length of longest audio sequence")
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
        log_step_count_steps=1,
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
            input_fn=create_input_fn(max_label_sequence_length=args.max_label_sequence_length,
                                     max_audio_sequence_length=args.max_audio_sequence_length,
                                     mode=tf.estimator.ModeKeys.TRAIN,
                                     input_prefix=args.train_prefix,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size,
                                     sample_rate=args.sample_rate),
            max_steps=args.max_steps,
        )

        eval_spec = tf.estimator.EvalSpec(
            steps=args.eval_every,
            input_fn=create_input_fn(max_label_sequence_length=args.max_label_sequence_length,
                                     max_audio_sequence_length=args.max_audio_sequence_length,
                                     mode=tf.estimator.ModeKeys.EVAL,
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
