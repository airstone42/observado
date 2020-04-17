#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

import observado.lib.utils as utils


def _load_data(wav_path) -> np.ndarray:
    major = utils.chord_table['M']
    minor = utils.chord_table['m']
    weights = np.zeros((25, 12), dtype=float)
    for c in range(12):
        weights[c, :] = np.roll(major, c)
        weights[c + 12, :] = np.roll(minor, c)
    weights[-1] = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.]) / 4.
    return weights


def analyze_hmm(chroma: np.ndarray, show=False) -> (list, list, list):
    weights = _load_data(utils.enhanced_cqt)
    labels = [(lambda x, y: x + y if y != 'M' else x)(x, y) for y in ['M', 'm'] for x in utils.all_notes if
              x not in utils.note_alts.keys()]
    labels.append('N')
    trans = librosa.sequence.transition_loop(25, 0.9)

    probs = np.exp(weights.dot(chroma))
    probs /= probs.sum(axis=0, keepdims=True)
    chords_ind = np.argmax(probs, axis=0)
    chords_vit = librosa.sequence.viterbi_discriminative(probs, trans)

    if show:
        show_hmm(chroma, weights, labels, probs, chords_vit, chords_ind)

    frames = [x + 1 for x in range(len(chords_vit) - 1) if chords_vit[x] != chords_vit[x + 1]]
    frames.insert(0, 0)
    frames.append(len(chords_vit) - 1)
    chords = [labels[chords_vit[x]] for x in frames[:-1]]
    return chords, librosa.frames_to_time(frames), frames


def show_hmm(chroma, weights, labels, probs, chords_vit, chords_ind):
    plt.figure(figsize=(10, 12))
    plt.subplot(2, 1, 1)
    librosa.display.specshow(chroma, x_axis='time', y_axis='chroma')
    plt.colorbar()
    plt.subplot(2, 1, 2)
    librosa.display.specshow(weights, x_axis='chroma')
    plt.yticks(np.arange(25) + 0.5, labels)
    plt.ylabel('Chord')
    plt.colorbar()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 12))
    librosa.display.specshow(probs, x_axis='time', cmap='gray')
    plt.colorbar()
    times = librosa.times_like(chords_vit)
    plt.scatter(times, chords_ind + 0.75, color='lime', alpha=0.5, marker='+', s=15, label='Independent')
    plt.scatter(times, chords_vit + 0.25, color='deeppink', alpha=0.5, marker='o', s=15, label='Viterbi')
    plt.yticks(0.5 + np.unique(chords_vit),
               [labels[i] for i in np.unique(chords_vit)], va='center')
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    y, _ = librosa.load(sys.argv[1] if len(sys.argv) > 1 else librosa.util.example_audio_file())
    y = librosa.effects.harmonic(y, margin=4)
    chroma = utils.chroma(y, 'cens')
    analyze_hmm(chroma, True)


if __name__ == '__main__':
    main()
