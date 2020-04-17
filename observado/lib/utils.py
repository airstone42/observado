import os
from typing import Optional

import librosa
import numpy as np
import scipy.ndimage
import scipy.stats

dirname = os.path.dirname(__file__)
basic = os.path.join(dirname, '../../data/features/basic.csv')
noise = os.path.join(dirname, '../../data/features/noise.csv')
enhanced_cqt = os.path.join(dirname, '../../data/features/wav_enhanced_cqt.csv')
cqt = os.path.join(dirname, '../../data/features/wav_cqt.csv')
stft = os.path.join(dirname, '../../data/features/wav_stft.csv')
cens = os.path.join(dirname, '../../data/features/wav_cens.csv')

note_values = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

note_alts = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

# Chord pattern for C
chord_table = {'M': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
               'm': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]),
               # 'aug': np.array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]),
               # 'dim': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]),
               '7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
               'm7': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]),
               'maj7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]),
               # 'dim7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]),
               # 'ø7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]),
               # '9': np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
               # 'add9': np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
               # 'add6': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]),
               # 'sus2': np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
               # 'sus4': np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]),
               }

all_notes = sorted(tuple(x for x in (x for x in (x for y in
                                                 ((chr(x), chr(x) + '#', chr(x) + 'b') for x in
                                                  range(ord('A'), ord('G') + 1)) for x in y))
                         if x not in ('B#', 'Cb', 'E#', 'Fb')),
                   key=lambda x, v=note_values, t=note_alts: v[x] if x not in t else v[t[x]])

# Calculate all chords by combine notes and chord patterns.
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in all_notes
              if x not in note_alts.keys() for y in chord_table.keys()]


# Compute a float number indicating BPM.
def tempo(y: np.ndarray, p=False) -> float:
    env = librosa.onset.onset_strength(y)
    prior = scipy.stats.uniform(30, 300)
    t = librosa.beat.tempo(onset_envelope=env) if not p else librosa.beat.tempo(onset_envelope=env, prior=prior)
    return t[0]


# Compute beat frames and beat time series.
def beats(y: np.ndarray) -> (np.ndarray, np.ndarray):
    env = librosa.onset.onset_strength(y, aggregate=np.median)
    _, b = librosa.beat.beat_track(onset_envelope=env)
    return b, librosa.frames_to_time(b)


# Compute chromagram
def chroma(y: np.ndarray, method) -> np.ndarray:
    methods = {'enhanced_cqt': _chroma_cqtx, 'cqt': _chroma_cqt, 'stft': _chroma_stft, 'cens': _chroma_cens}
    if method in methods.keys():
        return methods[method](y)
    else:
        return np.array([])


# Compute enhanced chromagram with CQT
def _chroma_cqtx(y: np.ndarray) -> np.ndarray:
    y = librosa.feature.chroma_cqt(y=y, bins_per_octave=36)
    y = np.minimum(y, librosa.decompose.nn_filter(y, aggregate=np.median, metric='cosine'))
    y = scipy.ndimage.median_filter(y, size=(1, 9))
    return y


def _chroma_cqt(y: np.ndarray) -> np.ndarray:
    return librosa.feature.chroma_cqt(y=y)


def _chroma_stft(y: np.ndarray) -> np.ndarray:
    return librosa.feature.chroma_stft(y=y)


def _chroma_cens(y: np.ndarray) -> np.ndarray:
    return librosa.feature.chroma_cens(y=y, bins_per_octave=36)


# Compute the mean of each piece of chromagram according to beat frames segmentation
def means(chromagram: np.ndarray, beat_frames: Optional[np.ndarray] = None) -> np.ndarray:
    if beat_frames is not None:
        beat_frames = np.insert(beat_frames, 0, 0)
        beat_frames = np.append(beat_frames, len(chromagram[0]) - 1)
        return np.array(
            [[chromagram[i][beat_frames[j]:beat_frames[j + 1]].mean()
              for j in range(len(beat_frames) - 1)] for i in range(len(chromagram))])
    else:
        return np.array([chromagram[i].mean() for i in range(len(chromagram))])
