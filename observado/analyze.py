#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier

import observado.lib.utils as utils
from observado.lib.chords import Chord

dirname = os.path.dirname(__file__)
chord_table = {k: v for (k, v) in utils.chord_table.items()}
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y)
              for x in utils.all_notes if x not in utils.note_alts.keys() for y in chord_table.keys()]

roots = dict(zip([x for x in utils.all_notes if x not in utils.note_alts.keys()], [y for y in range(12)]))
qualities = dict(zip([x for x in chord_table.keys()], [y for y in range(len(chord_table))]))
qualities['N'] = len(chord_table)
chords = dict(zip([x for x in all_chords], [y for y in range(len(all_chords))]))
chords['N'] = len(chords)


def _get_quality(n: int) -> str:
    return '' if list(qualities.keys())[n] == 'M' else list(qualities.keys())[n]


def _load_data(maj: True, wav_path=utils.cens, noise_path=utils.noise) -> (np.ndarray, np.ndarray, np.ndarray):
    df = pd.read_csv(wav_path, usecols=lambda col: col != 'method')
    df = df.append(pd.read_csv(noise_path), sort=False)
    head = list(df.head())
    # Read the number of roots and qualities for chords from CSV file.
    # Major or minor third depends on parameter "maj".
    a = np.array(
        [(x[head.index('C'):head.index('B') + 1], roots[x[head.index('root')]], qualities[x[head.index('quality')]]) for
         x in df.values if
         x[head.index('notation')] in chords.keys() and x[head.index('root')] != 'N' and x[head.index('quality')] in (
             ('M', '7', 'maj7') if maj else ('m', 'm7'))])
    np.random.shuffle(a)
    x = np.array([x[0] for x in a], dtype=np.float)
    y = np.array([x[1] for x in a])
    z = np.array([x[2] for x in a])
    return x, y, z


def _train(maj: True):
    x_full, y_full, z_full = _load_data(maj)
    x_train, y_train, z_train = \
        x_full[:int(0.8 * len(x_full))], y_full[:int(0.8 * len(y_full))], z_full[:int(0.8 * len(z_full))]
    x_test, y_test, z_test = \
        x_full[int(0.8 * len(x_full)):], y_full[int(0.8 * len(y_full)):], z_full[int(0.8 * len(z_full)):]

    if os.path.exists(os.path.join(dirname, '../data/models/major.joblib')) and os.path.exists(
            os.path.join(dirname, '../data/models/minor.joblib')):
        for i in range(len(x_test)):
            x_test[i] = np.roll(x_test[i], -y_test[i])
        if maj:
            maj_clf = joblib.load(os.path.join(dirname, '../data/models/major.joblib'))
            print(accuracy_score(z_test, maj_clf.predict(x_test)))
        else:
            min_clf = joblib.load(os.path.join(dirname, '../data/models/minor.joblib'))
            print(accuracy_score(z_test, min_clf.predict(x_test)))
        return

    assert len(x_train) == len(y_train) == len(z_train)
    for i in range(len(x_train)):
        x_train[i] = np.roll(x_train[i], -y_train[i])
    assert len(x_test) == len(y_test) == len(z_test)
    for i in range(len(x_test)):
        x_test[i] = np.roll(x_test[i], -y_test[i])

    clf = KNeighborsClassifier()
    clf.fit(x_train, z_train)
    print(accuracy_score(z_test, clf.predict(x_test)))
    joblib.dump(clf,
                os.path.join(dirname, '../data/models/major.joblib' if maj else '../data/models/minor.joblib'))


def analyze_chords(chroma: np.ndarray, root: str, maj: bool):
    if not os.path.exists(os.path.join(dirname, '../data/models/major.joblib')) and os.path.exists(
            os.path.join(dirname, '../data/models/minor.joblib')):
        _train(True)
        _train(False)

    maj_clf = joblib.load(os.path.join(dirname, '../data/models/major.joblib'))
    min_clf = joblib.load(os.path.join(dirname, '../data/models/minor.joblib'))
    for i in range(len(chroma)):
        chroma[i] = np.roll(chroma[i], -utils.note_values[root])
    prob = maj_clf.predict(chroma) if maj else min_clf.predict(chroma)

    return root + _get_quality(prob[0])


def analyze(chroma: np.ndarray, hmm_chords: list, frames: list) -> list:
    data = []
    average = np.array([chroma.transpose()[frames[i]:frames[i + 1]].mean(axis=0) for i in range(len(frames) - 1)])
    for i in range(len(hmm_chords)):
        if hmm_chords[i] == 'N':
            data.append('N')
            continue
        chord = Chord(hmm_chords[i])
        data.append(analyze_chords(np.array([average[i]]), str(chord.root), chord.quality in ('M', '7', 'maj7')))
    return data


def main():
    _train(True)
    _train(False)


if __name__ == '__main__':
    main()
