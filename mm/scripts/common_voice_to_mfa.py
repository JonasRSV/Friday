import pathlib
import sox
import argparse
import os
import pandas as pd
from tqdm import tqdm

def normalize_transcription(transcription):
    transcription = transcription.replace('"', '')
    transcription = transcription.replace("'", '')
    transcription = transcription.replace(".", '')
    transcription = transcription.replace(",", '')
    transcription = transcription.replace("!", '')
    transcription = transcription.replace("?", '')
    return transcription.upper()

def convert_cv(transformer: sox.Transformer,
               max_per_speaker: int,
               tsv: pathlib.Path,
               clips: pathlib.Path,
               sink: pathlib.Path,
               prefix: str):

    meta = pd.read_csv(tsv, delimiter="\t")

    for client, df in tqdm(meta.groupby(by="client_id")):
        df = df.tail(max_per_speaker)

        speaker_sink = sink / client

        if not speaker_sink.is_dir():
            os.makedirs(speaker_sink)

        for audio, transcription in zip(df["path"], df["sentence"]):

            try:
                audio_without_stem = audio.split(".")[0]

                input_audio_file = clips / audio
                output_audio_file = speaker_sink / f"{prefix}-{audio_without_stem}.wav"

                output_transcription_file = speaker_sink / f"{prefix}-{audio_without_stem}.lab"


                transformer.build_file(input_filepath=str(input_audio_file), output_filepath=str(output_audio_file))
                with open(str(output_transcription_file), "w") as o:
                    transcription = normalize_transcription(transcription)
                    o.write(transcription)
            except Exception as e:
                print(f"Failed to convert audio {audio} with sentence {transcription} reason: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsv", type=pathlib.Path, help="tsv dataset")
    parser.add_argument("--clips", type=pathlib.Path, help="source of clips")
    parser.add_argument("--sink", type=pathlib.Path, help="where to write mfa dataset")
    parser.add_argument("--prefix", type=str, help="prefix of dataset")
    parser.add_argument("--max_per_speaker", type=int, help="max data per speaker")
    parser.add_argument("--sample_rate", type=int, help="resampling rate", default=16000)

    args = parser.parse_args()

    transformer = sox.Transformer()
    transformer.set_output_format(rate=args.sample_rate, channels=1)

    convert_cv(transformer, args.max_per_speaker, args.tsv, args.clips, args.sink, args.prefix)
