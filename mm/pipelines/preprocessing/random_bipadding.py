import numpy as np

def bipadding(length: float, audio: np.ndarray, sample_rate: int) -> np.ndarray:
    pad_to = int(sample_rate * length)
    num_padding = pad_to - len(audio)

    padding = list(np.random.normal(0, 10, size=num_padding).astype(np.int64))

    padding_split = np.random.randint(0, num_padding)

    head_padding = padding[:padding_split]
    tail_padding = padding[padding_split:]

    head_padding.extend(audio)
    head_padding.extend(tail_padding)

    return head_padding


