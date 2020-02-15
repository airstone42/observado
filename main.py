#!/usr/bin/env python3
import sys
from functools import reduce

import librosa
import numpy as np

from observado.analyze import analyze_root, analyze_chords
from observado.lib import utils


def calc(chroma: np.ndarray, beats: np.ndarray) -> (list, list):
    roots = [(lambda x: x)(x) for x in analyze_root(chroma)]
    roots = [(lambda m: max(set(m), key=m.count))(roots[beats[j]:beats[j + 1]]) for j in range(len(beats) - 1)]
    root_parted = [beats[i + 1] for i in range(len(roots) - 1) if roots[i] != roots[i + 1]]
    root_parted.insert(0, 0)
    root_parted.append(beats[-1])

    average = np.array([chroma[root_parted[i]:root_parted[i + 1]].mean(axis=0) for i in range(len(root_parted) - 1)])
    roots = reduce(lambda y, x: x == y[-1] and y or y + [x], roots, [roots[0]])

    chords = analyze_chords(average, roots)
    return chords, librosa.frames_to_time(root_parted)


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else librosa.util.example_audio_file()
    y, _ = librosa.load(filename)
    b, t = utils.beats(y)
    y = utils.chroma(y, 'cqt')
    b = np.insert(b, 0, 0)
    b = np.append(b, y.shape[1] - 1)
    chords, time_frames = calc(y.transpose(), b)
    for i in range(len(time_frames) - 1):
        print('{:.4f}-{:.4f}: {}'.format(time_frames[i], time_frames[i + 1], chords[i]))


if __name__ == '__main__':
    main()
