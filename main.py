#!/usr/bin/env python3
import sys

import librosa
import numpy as np

from src import utils
from src.chords import Chord
from src.analyze import analyze


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else librosa.util.example_audio_file()
    y, _ = librosa.load(filename)
    b, t = utils.beats(y)
    y = utils.chroma_cens(y)
    b = np.insert(b, 0, 0)
    b = np.append(b, y.shape[1] - 1)
    chords = analyze(y.transpose())
    chords = [(lambda m: max(set(m), key=m.count))(chords[b[j]:b[j + 1]]) for j in range(len(b) - 1)]
    for i in t:
        print('%.2f' % i, end='    ')
    print()
    for i in chords:
        print('%s' % i.notation if isinstance(i, Chord) else i , end='    ')


if __name__ == '__main__':
    main()
