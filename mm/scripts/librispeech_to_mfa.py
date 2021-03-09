import pathlib
import sox
import argparse
import os
from tqdm import tqdm


def locate_transcriptions(chapter_root: pathlib.Path):
    transcriptions = list(chapter_root.glob("*.trans.txt"))

    if len(transcriptions) > 0:
        return transcriptions[0]
    else:
        return None


def convert_chapter(path: pathlib.Path, sink: pathlib.Path, prefix: str,
                    transformer: sox.Transformer):
    transcriptions = locate_transcriptions(path)

    if not sink.is_dir():
        os.makedirs(sink)

    if transcriptions:
        with open(str(transcriptions), "r") as transcriptions:
            for line in transcriptions.readlines():
                line = line.strip()
                end_of_index = line.find(" ")

                file_name = line[:end_of_index].strip()

                file_name_with_extension = file_name + ".flac"

                audio_input_file = path / file_name_with_extension

                audio_output_file = sink / f"{prefix}-{file_name}.wav"
                label_output_file = sink / f"{prefix}-{file_name}.lab"

                label = line[end_of_index:].strip()

                transformer.build_file(input_filepath=str(audio_input_file), output_filepath=str(audio_output_file))

                with open(str(label_output_file), "w") as label_file:
                    label_file.write(label)


def convert_speaker(path: pathlib.Path, sink: pathlib.Path, prefix: str,
                    transformer: sox.Transformer):
    for chapter_path in path.glob("*"):
        if str(chapter_path.stem).isnumeric():
            convert_chapter(chapter_path, sink, prefix, transformer)


def convert_speakers(path: pathlib.Path, sink: pathlib.Path, prefix: str):
    transformer = sox.Transformer()
    for speaker_path in tqdm(list(path.glob("*"))):
        if str(speaker_path.stem).isnumeric():
            sub_sink = sink / speaker_path.stem

            convert_speaker(speaker_path, sub_sink, prefix, transformer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, help="source librispeech dataset")
    parser.add_argument("--sink", type=pathlib.Path, help="where to write mfa dataset")
    parser.add_argument("--prefix", type=str, help="prefix of dataset")

    args = parser.parse_args()

    convert_speakers(args.source, args.sink, args.prefix)
