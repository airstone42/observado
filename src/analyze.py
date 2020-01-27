#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Dense, Input, concatenate
from keras.models import Model
from tensorflow import keras

import src.utils as utils
from src.chords import Chord

tf.keras.backend.clear_session()

excepted = ()
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
        x_full[:int(0.7 * len(x_full))], y_full[:int(0.7 * len(y_full))], z_full[:int(0.7 * len(z_full))]
    x_valid, y_valid, z_valid = \
        x_full[int(0.7 * len(x_full)):int(0.9 * len(x_full))], y_full[int(0.7 * len(y_full)):int(0.9 * len(y_full))], \
        z_full[int(0.7 * len(z_full)):int(0.9 * len(z_full))]
    x_test, y_test, z_test = \
        x_full[int(0.9 * len(x_full)):], y_full[int(0.9 * len(y_full)):], z_full[int(0.9 * len(z_full)):]

    if os.path.exists(os.path.join(dirname, '../data/models/model.h5')):
        model = keras.models.load_model(os.path.join(dirname, '../data/models/model.h5'))
        print(model.evaluate(x_test, [y_test, z_test]))
        return

    chord_input = Input(shape=(12,), dtype=float, name='chord_input')
    x = Dense(600, activation='relu')(chord_input)
    x = Dense(300, activation='relu')(x)
    root_output = Dense(len(roots), activation='softmax')(x)
    y = concatenate([chord_input, root_output])
    y = Dense(6000, activation='relu')(y)
    y = Dense(3000, activation='relu')(y)
    y = Dense(1000, activation='relu')(y)
    quality_output = Dense(len(qualities), activation='softmax')(y)

    model = Model(inputs=chord_input, outputs=[root_output, quality_output])
    model.compile(loss="sparse_categorical_crossentropy", optimizer="sgd", metrics=["accuracy"])
    model.fit(x_train, [y_train, z_train], epochs=100, validation_data=(x_valid, [y_valid, z_valid]))

    print(model.evaluate(x_test, [y_test, z_test]))
    model.save(os.path.join(dirname, '../data/models/model.h5'))


def analyze(y: np.ndarray) -> list:
    def get_root(n: np.ndarray) -> str:
        return list(roots.keys())[n.argmax()]

    def get_quality(n: np.ndarray) -> str:
        return '' if list(qualities.keys())[n.argmax()] == 'M' else list(qualities.keys())[n.argmax()]

    model = keras.models.load_model(os.path.join(dirname, '../data/models/model.h5'))
    y_prob = model.predict(y)
    root_prob, quality_prob = y_prob[0], y_prob[1]
    assert len(root_prob) == len(quality_prob)
    pred = [(lambda a, b: 'N' if a == 'N' or b == 'N' else Chord(a + b))
            (get_root(root_prob[i]), get_quality(quality_prob[i])) for i in range(len(root_prob))]
    return pred


def main():
    _train()


if __name__ == '__main__':
    main()
