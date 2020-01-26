#!/usr/bin/env python3
import sys

import librosa

from src import utils
from src.analyze import analyze


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else librosa.util.example_audio_file()
    y, _ = librosa.load(filename)
    b, t = utils.beats(y)
    y = utils.chroma_cens(y)
    y = utils.means(y, b).transpose()
    chords = analyze(y)
    for i in t:
        print('%.2f' % i, end='    ')
    print()
    for i in chords:
        print('%s' % i.notation, end='    ')


if __name__ == '__main__':
    main()
