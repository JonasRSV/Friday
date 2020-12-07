"""This module implements extraction of logmel features from a raw audio signal"""
import tensorflow as tf


def normalize_audio(signal: tf.Tensor):
    return tf.cast(signal, tf.float32) / 32768.0


def normalize_mfcc(mfcc: tf.Tensor) -> tf.Tensor:
    # These values are from manually inspecting spectrograms using the friday_inspect.py
    # We do this to try to standardize our data a bit, NN's work better with data
    # centered around 0 with not too high std.
    MFCC_MEAN, MFCC_STD = tf.constant(125.0), tf.constant(150.0)
    return mfcc #- MFCC_MEAN) / MFCC_STD


def normalize_mel_spectrogram(spectrogram: tf.Tensor):
    # These values are from manually inspecting spectrograms using the friday_inspect.py
    # We do this to try to standardize our data a bit, NN's work better with data
    # centered around 0 with not too high std.

    return spectrogram / tf.constant(10.0)


def mfcc_feature(signal: tf.Tensor, coefficients: int,
                 frame_length=1024, frame_step=256,
                 fft_length=1024,
                 sample_rate=44100,
                 lower_edge_hertz=80.0,
                 upper_edge_hertz=7600.0,
                 num_mel_bins=40):
    """Computes 'coefficient' MFCC coefficient from the audio signal

    Args:
        signal: a batch float tensor [batch_size, clip_length] with values in [-1, 1] representing the audio signal
        coefficients: The number of MFCC coefficients to extract
        frame_length: Length of short time FFT frame
        frame_step: Length of frame step
        fft_length: Length of FFT time
        sample_rate: Sample rate of audio signal
        lower_edge_hertz: Lower-bound of frequencies to include in signal
        upper_edge_hertz: Upper-bound of frequencies to include in signal
        num_mel_bins: Bands in the mel spectrum
    """

    # Short time fourier transform across the signal
    stfts = tf.signal.stft(signal,
                           frame_length=frame_length,
                           frame_step=frame_step,
                           fft_length=fft_length)

    # Turn into spectrograms
    spectrograms = tf.abs(stfts)

    # Calculate mel features
    num_spectrogram_bins = stfts.shape[-1].value
    linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=num_mel_bins, num_spectrogram_bins=num_spectrogram_bins,
        sample_rate=sample_rate,
        lower_edge_hertz=lower_edge_hertz,
        upper_edge_hertz=upper_edge_hertz)
    mel_spectrograms = tf.tensordot(
        spectrograms, linear_to_mel_weight_matrix, 1)
    mel_spectrograms.set_shape(spectrograms.shape[:-1].concatenate(
        linear_to_mel_weight_matrix.shape[-1:]))

    # Log-mel trick
    log_mel_spectrograms = tf.math.log(mel_spectrograms + 1e-6)

    # Extract MFCC's
    return normalize_mfcc(tf.signal.mfccs_from_log_mel_spectrograms(
        log_mel_spectrograms)[..., :coefficients])


def mel_spectrogram_feature(signal: tf.Tensor,
                            frame_length=1024,
                            frame_step=256,
                            fft_length=1024,
                            sample_rate=8000,
                            lower_edge_hertz=80.0,
                            upper_edge_hertz=7600.0,
                            num_mel_bins=40):
    """Computes the mel spectrograms of an audio signal

    Args:
        signal: a batch float tensor [batch_size, clip_length] with values in [-1, 1] representing the audio signal
        coefficients: The number of MFCC coefficients to extract
        frame_length: Length of short time FFT frame
        frame_step: Length of frame step
        fft_length: Length of FFT time
        sample_rate: Sample rate of audio signal
        lower_edge_hertz: Lower-bound of frequencies to include in signal
        upper_edge_hertz: Upper-bound of frequencies to include in signal
        num_mel_bins: Bands in the mel spectrum
    """

    # Short time fourier transform across the signal
    stfts = tf.signal.stft(signal,
                           frame_length=frame_length,
                           frame_step=frame_step,
                           fft_length=fft_length)

    # Turn into spectrograms
    spectrograms = tf.abs(stfts)

    # Calculate mel features
    num_spectrogram_bins = stfts.shape[-1].value
    linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins=num_mel_bins, num_spectrogram_bins=num_spectrogram_bins,
        sample_rate=sample_rate,
        lower_edge_hertz=lower_edge_hertz,
        upper_edge_hertz=upper_edge_hertz)
    mel_spectrograms = tf.tensordot(
        spectrograms, linear_to_mel_weight_matrix, 1)
    mel_spectrograms.set_shape(spectrograms.shape[:-1].concatenate(
        linear_to_mel_weight_matrix.shape[-1:]))

    return normalize_mel_spectrogram(mel_spectrograms)
