#!/usr/bin/env python3
import sys

import librosa

from observado.analyze import analyze
from observado.hmm import analyze_hmm
from observado.lib import utils


def run(filename: str) -> str:
    if not filename:
        filename = librosa.util.example_audio_file()
    y, _ = librosa.load(filename)
    y = librosa.effects.harmonic(y, margin=4)
    chroma = utils.chroma(y, 'cens')
    # HMM analyze basic chord types (major or minor) and lasting time
    chords, time_frames, frames = analyze_hmm(chroma)
    # Analyze the seventh intervals
    chords = analyze(chroma, chords, frames)
    s = ''
    for i in range(len(time_frames) - 1):
        s += '{:.2f} {:.2f} {}'.format(time_frames[i], time_frames[i + 1], chords[i])
        if i != len(time_frames) - 2:
            s += '\n'
    return s


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else librosa.util.example_audio_file()
    print(run(filename))


if __name__ == '__main__':
    main()
