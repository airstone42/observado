import librosa
import numpy as np
import scipy.ndimage
import scipy.stats

HARMONIC_MARGIN = 8
CQT_MARGIN = 36

note_values = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

note_alts = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

# Chord pattern for C
chord_table = {'M': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
               'm': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]),
               'aug': np.array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]),
               'dim': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]),
               '7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
               'm7': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]),
               'maj7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]),
               'dim7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]),
               'ø7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]),
               '9': np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
               'add9': np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
               'add6': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]),
               'sus2': np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
               'sus4': np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]), }

all_notes = sorted(tuple(x for x in (x for x in (x for y in ((chr(x), chr(x) + '#', chr(x) + 'b') for x in
                                                             range(ord('A'), ord('G') + 1)) for x in y)) if
                         x not in ('B#', 'Cb', 'E#', 'Fb')),
                   key=lambda x, v=note_values, t=note_alts: v[x] if x not in t else v[t[x]])

# Calculate all chords by combine notes and chord patterns.
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in all_notes if x not in note_alts.keys() for y in
              chord_table.keys()]


def load(filename: str) -> np.ndarray:
    return librosa.load(filename)[0]


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


# Compute enhanced chromagram with CQT
def chroma_cqtx(y: np.ndarray) -> np.ndarray:
    y_harm = librosa.effects.harmonic(y=y, margin=HARMONIC_MARGIN)
    chroma = librosa.feature.chroma_cqt(y=y_harm, bins_per_octave=CQT_MARGIN)
    chroma = np.minimum(chroma, librosa.decompose.nn_filter(chroma, aggregate=np.median, metric='cosine'))
    chroma = scipy.ndimage.median_filter(chroma, size=(1, 9))
    return chroma


def chroma_cqt(y: np.ndarray) -> np.ndarray:
    return librosa.feature.chroma_cqt(y=y)


def chroma_stft(y: np.ndarray) -> np.ndarray:
    return librosa.feature.chroma_stft(y=y)


def chroma_cens(y: np.ndarray) -> np.ndarray:
    return librosa.feature.chroma_cens(y=y, cqt_mode='hybrid')
