#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals

import os

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

import src.utils as utils

tf.keras.backend.clear_session()

dirname = os.path.dirname(__file__)
chords = dict(zip([x for x in utils.all_chords], [y for y in range(len(utils.all_chords))]))
chords['N'] = 168

basic = os.path.join(dirname, '../data/features/basic.csv')
noise = os.path.join(dirname, '../data/features/noise.csv')
enhanced_cqt = os.path.join(dirname, '../data/features/wav_enhanced_cqt.csv')
cqt = os.path.join(dirname, '../data/features/wav_cqt.csv')
stft = os.path.join(dirname, '../data/features/wav_stft.csv')
cens = os.path.join(dirname, '../data/features/wav_cens.csv')


def load_data(wav_path, noise_path=noise) -> (np.ndarray, np.ndarray):
    df = pd.read_csv(wav_path, usecols=lambda col: col != 'method')
    df = df.append(pd.read_csv(noise_path), sort=False)
    head = list(df.head())
    need = chords
    # a = np.array([(x[head.index('C'):head.index('B') + 1], need[x[head.index('quality')]]) for x in df.values if
    #               x[head.index('quality')] in need.keys()])
    a = np.array([(x[head.index('C'):head.index('B') + 1], need[x[head.index('notation')]]) for x in df.values if
                  x[head.index('notation')] in need.keys()])
    np.random.shuffle(a)
    x = np.array([x[0] for x in a], dtype=np.float)
    y = np.array([x[1] for x in a])
    return x, y


def train():
    x, y = load_data(enhanced_cqt)
    x_train, y_train = x[:int(0.7 * len(x))], y[:int(0.7 * len(y))]
    x_valid, y_valid = x[int(0.7 * len(x)):int(0.9 * len(x))], y[int(0.7 * len(y)):int(0.9 * len(y))]
    x_test, y_test = x[int(0.9 * len(x)):], y[int(0.9 * len(y)):]

    if os.path.exists(os.path.join(dirname, '../data/models/model.h5')):
        model = keras.models.load_model(os.path.join(dirname, '../data/models/model.h5'))
        print(model.evaluate(x_test, y_test))
        return

    model = keras.models.Sequential([
        keras.layers.Flatten(input_shape=[12]),
        keras.layers.Dense(6000, activation="relu"),
        keras.layers.Dense(3000, activation="relu"),
        keras.layers.Dense(3000, activation="relu"),
        keras.layers.Dense(400, activation="softmax")
    ])
    model.compile(loss="sparse_categorical_crossentropy", optimizer="sgd", metrics=["accuracy"])
    model.fit(x_train, y_train, epochs=300, validation_data=(x_valid, y_valid))
    print(model.evaluate(x_test, y_test))
    model.save(os.path.join(dirname, '../data/models/model.h5'))


def analyze():
    model = keras.models.load_model(os.path.join(dirname, '../data/models/model.h5'))
    pred = pd.read_csv(basic)
    head = list(pred.head())
    a = np.array([(x[head.index('C'):head.index('B') + 1], x[head.index('notation')]) for x in pred.values if
                  x[head.index('notation')] in chords.keys()])
    np.random.shuffle(a)
    y = np.array([x[1] for x in a])
    x_pred = np.array([x[0] for x in a], dtype=np.float)
    y_pred = [list(chords.keys())[list(chords.values()).index(x)] for x in model.predict_classes(x_pred)]
    a = [(x, y) for x, y in list(zip(y, y_pred)) if x != y]
    print(a)


def main():
    train()
    analyze()


if __name__ == '__main__':
    main()
