import librosa
import numpy as np


def analyze_voice(audio_file):

    y, sr = librosa.load(audio_file, sr=None)

    duration = librosa.get_duration(
        y=y,
        sr=sr
    )

    if duration <= 0:
        duration = 1

    rms = librosa.feature.rms(y=y)

    average_volume = float(
        np.mean(rms)
    )

    zero_crossing_rate = librosa.feature.zero_crossing_rate(y)

    average_zcr = float(
        np.mean(zero_crossing_rate)
    )

    return {
        "duration": round(duration, 2),
        "average_volume": round(average_volume, 4),
        "zero_crossing_rate": round(average_zcr, 4)
    }