"""Download sounds from https://www.soundsnap.com/."""
import numpy as np
import pathlib
import sox


from models.shared.augmentations.core import Augmentation


class Background(Augmentation):

    def __init__(self,
                 background_noises: pathlib.Path,
                 sample_rate: int,
                 min_voice_factor: float,
                 max_voice_factor: float):

        if not background_noises.is_dir():
            raise Exception(f"{background_noises} is not a valid directory")

        self.normalization = 2 ** 15
        self.sample_rate = sample_rate
        self.min_voice_factor = min_voice_factor
        self.max_voice_factor = max_voice_factor

        self.noises, self.density = [], []

        transformer = sox.Transformer()
        transformer.set_output_format(rate=sample_rate, channels=1)
        for file in background_noises.glob("*.mp3"):
            print(f"Loading background noise {file}")
            resampled_audio = transformer.build_array(
                input_filepath=str(file), sample_rate_in=sample_rate, )

            self.noises.append(resampled_audio)
            self.density.append(len(resampled_audio))

        self.density = np.array(self.density)
        self.density = self.density / self.density.sum()

        self.clips = np.arange(len(self.noises))

    def apply(self, audio: np.ndarray, sample_rate: int):
        if self.sample_rate != sample_rate:
            raise Exception(f"Background noise mismatching sample rate {sample_rate} != {self.sample_rate}")

        voice_factor = np.random.uniform(self.min_voice_factor, self.max_voice_factor)
        clip = self.noises[np.random.choice(self.clips, p=self.density)]

        if len(clip) > len(audio):
            start_clip = int(np.random.uniform(0, len(clip) - len(audio)))
            audio = audio * voice_factor + clip[start_clip: start_clip + len(audio)] * (1 - voice_factor)
        else:
            start_audio = int(np.random.uniform(0, len(audio) - len(clip)))
            audio[start_audio: start_audio + len(clip)] = \
                audio[start_audio: start_audio + len(clip)] * voice_factor + clip * (1 - voice_factor)

        return audio


