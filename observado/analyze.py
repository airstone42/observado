#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

import observado.lib.utils as utils
from observado.lib.chords import Chord

excepted = ('sus2', 'sus4', 'aug', 'dim', 'dim7', 'ø7')
chord_table = {k: v for (k, v) in utils.chord_table.items() if k not in excepted}
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in utils.all_notes if x not in utils.note_alts.keys()
              for y in chord_table.keys()]

roots = dict(zip([x for x in utils.all_notes if x not in utils.note_alts.keys()], [y for y in range(12)]))
roots['N'] = 12
qualities = dict(zip([x for x in chord_table.keys()], [y for y in range(len(chord_table))]))
qualities['N'] = len(chord_table)
chords = dict(zip([x for x in all_chords], [y for y in range(len(all_chords))]))
chords['N'] = len(chords)

dirname = os.path.dirname(__file__)
basic = os.path.join(dirname, '../data/features/basic.csv')
noise = os.path.join(dirname, '../data/features/noise.csv')
enhanced_cqt = os.path.join(dirname, '../data/features/wav_enhanced_cqt.csv')
cqt = os.path.join(dirname, '../data/features/wav_cqt.csv')
stft = os.path.join(dirname, '../data/features/wav_stft.csv')
cens = os.path.join(dirname, '../data/features/wav_cens.csv')


def _load_data(wav_path, noise_path=noise) -> (np.ndarray, np.ndarray, np.ndarray):
    df = pd.read_csv(wav_path, usecols=lambda col: col != 'method')
    df = df.append(pd.read_csv(noise_path), sort=False)
    head = list(df.head())
    a = np.array(
        [(x[head.index('C'):head.index('B') + 1], roots[x[head.index('root')]], qualities[x[head.index('quality')]]) for
         x in df.values if x[head.index('notation')] in chords.keys()])
    np.random.shuffle(a)
    x = np.array([x[0] for x in a], dtype=np.float)
    y = np.array([x[1] for x in a])
    z = np.array([x[2] for x in a])
    return x, y, z


def _train():
    x_full, y_full, z_full = _load_data(cens)
    x_train, y_train, z_train = \
        x_full[:int(0.8 * len(x_full))], y_full[:int(0.8 * len(y_full))], z_full[:int(0.8 * len(z_full))]
    x_test, y_test, z_test = \
        x_full[int(0.8 * len(x_full)):], y_full[int(0.8 * len(y_full)):], z_full[int(0.8 * len(z_full)):]

    if os.path.exists(os.path.join(dirname, '../data/models/root.joblib')) and os.path.exists(
            os.path.join(dirname, '../data/models/quality.joblib')):
        root_clf = joblib.load(os.path.join(dirname, '../data/models/root.joblib'))
        quality_clf = joblib.load(os.path.join(dirname, '../data/models/quality.joblib'))
        print(accuracy_score(y_test, root_clf.predict(x_test)))
        for i in range(len(x_test)):
            x_test[i] = np.roll(x_test[i], -y_test[i])
        print(accuracy_score(z_test, quality_clf.predict(x_test)))
        return

    root_clf = KNeighborsClassifier()
    root_clf.fit(x_train, y_train)
    print(accuracy_score(y_test, root_clf.predict(x_test)))
    joblib.dump(root_clf, os.path.join(dirname, '../data/models/root.joblib'))

    assert len(x_train) == len(y_train) == len(z_train)
    for i in range(len(x_train)):
        x_train[i] = np.roll(x_train[i], -y_train[i])
    assert len(x_test) == len(y_test) == len(z_test)
    for i in range(len(x_test)):
        x_test[i] = np.roll(x_test[i], -y_test[i])

    quality_clf = MLPClassifier(max_iter=500)
    quality_clf.fit(x_train, z_train)
    print(accuracy_score(z_test, quality_clf.predict(x_test)))
    joblib.dump(quality_clf, os.path.join(dirname, '../data/models/quality.joblib'))


def analyze(y: np.ndarray) -> list:
    def get_root(n: int) -> str:
        return list(roots.keys())[n]

    def get_quality(n: int) -> str:
        return '' if list(qualities.keys())[n] == 'M' else list(qualities.keys())[n]

    if not (os.path.exists(os.path.join(dirname, '../data/models/root.joblib')) and os.path.exists(
            os.path.join(dirname, '../data/models/quality.joblib'))):
        _train()

    root_clf = joblib.load(os.path.join(dirname, '../data/models/root.joblib'))
    quality_clf = joblib.load(os.path.join(dirname, '../data/models/quality.joblib'))
    root_prob = root_clf.predict(y)
    assert len(y) == len(root_prob)
    for i in range(len(y)):
        y[i] = np.roll(y[i], -root_prob[i])
    quality_prob = quality_clf.predict(y)

    assert len(root_prob) == len(quality_prob)
    pred = [(lambda a, b: 'N' if a == 'N' or b == 'N' else Chord(a + b))
            (get_root(root_prob[i]), get_quality(quality_prob[i])) for i in range(len(root_prob))]
    return pred


def main():
    _train()


if __name__ == '__main__':
    main()
