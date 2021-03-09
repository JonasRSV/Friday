import sys
import os

# Some systems don't use the launching directory as root
sys.path.append(os.getcwd())

import pathlib
import tensorflow as tf
import models.shared.audio as audio
import argparse
import models.bulbasaur.architechtures as arch
import numpy as np
import models.shared.augmentation as augmentation
import models.shared.augmentations as a
from enum import Enum

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)


class Mode(Enum):
    train_eval = "train_eval"
    export = "export"


def create_input_fn(mode: tf.estimator.ModeKeys,
                    input_prefix: str,
                    audio_length: int,
                    sample_rate: int,
                    parallel_reads: int = 5,
                    batch_size: int = 32):
    feature_description = {
        'anchor': tf.io.FixedLenFeature([audio_length], tf.int64),
        'positive': tf.io.FixedLenFeature([audio_length], tf.int64),
        'negative': tf.io.FixedLenFeature([audio_length], tf.int64),
    }

    def decode_example(x):
        return tf.io.parse_single_example(x, feature_description)

    def cast_to_int16(x):
        x["anchor"] = tf.cast(x["anchor"], tf.int16)
        x["positive"] = tf.cast(x["positive"], tf.int16)
        x["negative"] = tf.cast(x["negative"], tf.int16)
        return x

    augmenter = augmentation.create_audio_augmentations([
        a.TimeStretch(min_rate=0.93, max_rate=0.98),
        a.PitchShift(min_semitones=-2, max_semitones=3),
        a.Shift(min_rate=-500, max_rate=500),
        a.Gain(min_gain=0.2, max_gain=2.0),
        a.Background(background_noises=pathlib.Path(f"{os.getenv('FRIDAY_DATA', default='data')}/background_noise"),
                     sample_rate=8000,
                     min_voice_factor=0.5,
                     max_voice_factor=0.8),
        a.GaussianNoise(loc=0, stddev=100)
    ],
        p=[
            0.5,
            0.5,
            0.3,
            0.1,
            1.0,
            0.5
        ]
    )

    def numpy_augment_audio(sounds: np.ndarray):
        augmented_sounds = []
        for sound in sounds:
            augmented_sounds.append(augmenter(sound, sample_rate=sample_rate))

        return np.array(augmented_sounds, dtype=np.int16)

    def augment_sounds(x):
        x["anchor"] = tf.numpy_function(numpy_augment_audio, inp=[x["anchor"]], Tout=tf.int16)
        x["positive"] = tf.numpy_function(numpy_augment_audio, inp=[x["positive"]], Tout=tf.int16)
        x["negative"] = tf.numpy_function(numpy_augment_audio, inp=[x["negative"]], Tout=tf.int16)

        x["anchor"] = tf.reshape(x["anchor"], [-1, audio_length])
        x["positive"] = tf.reshape(x["positive"], [-1, audio_length])
        x["negative"] = tf.reshape(x["negative"], [-1, audio_length])

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
            # If we train we do data augmentation
            dataset = dataset.shuffle(buffer_size=100)

        dataset = dataset.batch(batch_size=batch_size)

        if mode == tf.estimator.ModeKeys.TRAIN:
            dataset = dataset.repeat()

            dataset = dataset.map(augment_sounds)

        return dataset

    return input_fn


def cosine_distance(a: tf.Tensor, b: tf.Tensor):
    return 1 - tf.reduce_sum(a * b, axis=-1)


def triplet_loss(anchor_embeddings: tf.Tensor,
                 positive_embeddings: tf.Tensor,
                 negative_embeddings: tf.Tensor,
                 margin=1.0):
    anchor_embeddings = tf.linalg.l2_normalize(anchor_embeddings, axis=1)
    positive_embeddings = tf.linalg.l2_normalize(positive_embeddings, axis=1)
    negative_embeddings = tf.linalg.l2_normalize(negative_embeddings, axis=1)

    triplet = tf.nn.relu(cosine_distance(anchor_embeddings, positive_embeddings) -
                         cosine_distance(anchor_embeddings, negative_embeddings) + margin)

    # return similarity_loss(left_embeddings, right_embeddings)
    return tf.reduce_sum(triplet)


def get_predict_ops(stored_embeddings: tf.Tensor,
                    signal_embeddings: tf.Tensor):

    similarities = 1 - cosine_distance(stored_embeddings, signal_embeddings)
    predict_op = tf.argmax(similarities)
    return predict_op, similarities


def get_metric_ops(anchor_embeddings: tf.Tensor,
                   positive_embeddings: tf.Tensor,
                   negative_embeddings: tf.Tensor,
                   margin: float):
    metric_ops = {}
    loss_op = triplet_loss(anchor_embeddings, positive_embeddings, negative_embeddings, margin)

    return loss_op, metric_ops


def get_train_ops(anchor_embeddings: tf.Tensor,
                  positive_embeddings: tf.Tensor,
                  negative_embeddings: tf.Tensor,
                  margin: float,
                  learning_rate: float,
                  save_summaries_every: int,
                  summary_output_dir: str):
    loss_op = triplet_loss(anchor_embeddings,
                           positive_embeddings,
                           negative_embeddings,
                           margin=margin)

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

    loss_op = tf.identity(loss_op, name="loss_op")

    train_logging_hooks = [
        tf.estimator.LoggingTensorHook(
            {"loss": "loss_op"},
            every_n_iter=1),
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
                  margin: float = 1.0,
                  sample_rate: int = 8000,
                  save_summaries_every: int = 100,
                  learning_rate: float = 0.001):
    def model_fn(features, labels, mode, config, params):
        print("features", features)
        loss_op, train_op, train_logging_hooks, eval_metric_ops, predict_op = None, None, None, None, None
        if mode == tf.estimator.ModeKeys.TRAIN:
            anchor_embeddings = get_embedding(features["anchor"],
                                              sample_rate=sample_rate,
                                              embedding_dim=embedding_dim,
                                              mode=mode)
            positive_embeddings = get_embedding(features["positive"],
                                                sample_rate=sample_rate,
                                                embedding_dim=embedding_dim,
                                                mode=mode)

            negative_embeddings = get_embedding(features["negative"],
                                                sample_rate=sample_rate,
                                                embedding_dim=embedding_dim,
                                                mode=mode)

            loss_op, train_op, train_logging_hooks = get_train_ops(
                anchor_embeddings=anchor_embeddings,
                positive_embeddings=positive_embeddings,
                negative_embeddings=negative_embeddings,
                margin=margin,
                learning_rate=learning_rate,
                save_summaries_every=save_summaries_every,
                summary_output_dir=summary_output_dir)
        elif mode == tf.estimator.ModeKeys.EVAL:
            anchor_embeddings = get_embedding(features["anchor"],
                                              sample_rate=sample_rate,
                                              embedding_dim=embedding_dim,
                                              mode=mode)
            positive_embeddings = get_embedding(features["positive"],
                                                sample_rate=sample_rate,
                                                embedding_dim=embedding_dim,
                                                mode=mode)

            negative_embeddings = get_embedding(features["negative"],
                                                sample_rate=sample_rate,
                                                embedding_dim=embedding_dim,
                                                mode=mode)

            loss_op, eval_metric_ops = get_metric_ops(anchor_embeddings=anchor_embeddings,
                                                      positive_embeddings=positive_embeddings,
                                                      negative_embeddings=negative_embeddings,
                                                      margin=margin)
        elif mode == tf.estimator.ModeKeys.PREDICT:
            embeddings = get_embedding(tf.expand_dims(features["audio"], 0),
                                       sample_rate=sample_rate,
                                       embedding_dim=embedding_dim,
                                       mode=mode)

            embeddings = tf.linalg.l2_normalize(embeddings, axis=1)

            predict_op, similarities_op = get_predict_ops(
                stored_embeddings=features["embeddings"],
                signal_embeddings=embeddings,
            )

            project_op = tf.squeeze(embeddings)

            tf.identity(project_op, name="project")
            tf.identity(tf.shape(project_op), name="project_shape")

            tf.identity(predict_op, name="output")
            tf.identity(tf.shape(predict_op), name="output_shape")

            tf.identity(similarities_op, name="similarities")
            tf.identity(tf.shape(similarities_op), name="similarities_shape")
        else:
            raise Exception(f"Unknown ModeKey {mode}")

        print('global vars', tf.global_variables())
        print('global vars', len(tf.global_variables()))
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
    parser.add_argument("--margin",
                        required=True,
                        type=float,
                        help="Margin for triplet loss")
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
            margin=args.margin,
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
                                     sample_rate=args.sample_rate,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size),
            max_steps=args.max_steps,
        )

        eval_spec = tf.estimator.EvalSpec(
            steps=args.eval_every,
            input_fn=create_input_fn(mode=tf.estimator.ModeKeys.EVAL,
                                     input_prefix=args.train_prefix,
                                     audio_length=int(args.clip_length * args.sample_rate),
                                     sample_rate=args.sample_rate,
                                     parallel_reads=args.parallel_reads,
                                     batch_size=args.batch_size),
            throttle_secs=5,
        )

        tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)

    elif args.mode == Mode.export.value:

        def serving_input_receiver_fn():
            audio_length = int(args.clip_length * args.sample_rate)
            inputs = {
                "audio": tf.placeholder(shape=[audio_length], dtype=tf.int16, name="audio"),
                "embeddings": tf.placeholder(shape=[None, args.embedding_dim], dtype=tf.float32, name="embeddings"),

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
