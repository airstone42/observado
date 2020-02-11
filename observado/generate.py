#!/usr/bin/env python3
import os
import random
import subprocess
from concurrent import futures

import librosa
import numpy as np
import pandas
from tqdm import tqdm

from observado.lib import utils
from observado.lib.midi import *

dirname = os.path.dirname(__file__)
all_notes = utils.all_notes
all_chords = utils.all_chords
noise = 0.3


def multi_run(function, iterator):
    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        result = list(tqdm(pool.map(function, iterator), total=len(iterator)))
    return result


def dir_check():
    def check_and_make(subdir):
        if not os.path.exists(os.path.join(dirname, subdir)):
            os.mkdir(os.path.join(dirname, subdir))

    print('Checking directories...')
    for i in ['../data', '../data/midi', '../data/waves', '../data/features']:
        check_and_make(i)

    if len(os.listdir(os.path.join(dirname, '../data/midi'))) == 0:
        open(os.path.join(dirname, '../data/midi/.gitkeep'), 'a').close()
    if len(os.listdir(os.path.join(dirname, '../data/waves'))) == 0:
        open(os.path.join(dirname, '../data/waves/.gitkeep'), 'a').close()


def basic_generate():
    if os.path.exists(os.path.join(dirname, '../data/features/basic.csv')):
        return

    data = []
    for i in all_chords:
        p = Pattern(i)
        if p.available:
            notes = [x for x in all_notes if x not in utils.note_alts.keys()]
            chroma = dict(zip(notes, p.array.tolist()))
            extra = {'notation': p.chord.notation, 'root': str(p.chord.root), 'quality': p.chord.quality,
                     'bass': str(p.chord.bass)}
            data.append({**chroma, **extra})
    try:
        with open(os.path.join(dirname, '../data/features/basic.csv'), 'xt', encoding="utf-8", newline='\n') as f:
            print('Generating basic patterns...')
            pandas.DataFrame(data).to_csv(f, index=False, line_terminator='\n')
    except FileExistsError:
        pass
    except Exception as e:
        raise e


def midi_generate():

    def generate(chord):
        for i in SingleChordContent.inst_table:
            for j in SingleChordContent.play_table.keys():
                p = SingleChordContent(chord, i, j)
                filename = p.pattern.chord.notation + '_' + str(p.inst) + '_' + str(p.method)
                p.write(os.path.join(dirname, '../data/midi/{}.mid'.format(filename)))

    dir_list = os.listdir(os.path.join(dirname, '../data/midi'))
    if (len(dir_list) != 0 and len(dir_list) != 1) or not (len(dir_list) == 1 and dir_list[0] == '.gitkeep'):
        return

    print('Generating MIDI files...')
    multi_run(generate, all_chords)


def wave_generate():
    def generate(chord):
        for i in SingleChordContent.inst_table:
            for j in SingleChordContent.play_table.keys():
                p = SingleChordContent(chord, i, j)
                filename = p.pattern.chord.notation + '_' + str(p.inst) + '_' + str(p.method)
                midi_name = os.path.join(dirname, '../data/midi/{}.mid'.format(filename))
                wave_name = os.path.join(dirname, '../data/waves/{}.wav'.format(filename))
                if not os.path.exists(wave_name):
                    # Problems when running on Windows for 'ø7' chord.
                    if 'ø7' in wave_name:
                        wave_name = wave_name.replace('ø7', 'm7b5')
                    subprocess.run([child, midi_name, '-Ow', '-o', wave_name], stdout=subprocess.DEVNULL)

    # Check timidity.
    child = 'timidity'
    try:
        subprocess.run([child], stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        try:
            child = 'timidity++'
            subprocess.run([child], stdout=subprocess.DEVNULL)
        except FileNotFoundError:
            print('Error when generating WAV files.')
            print('Make sure timidity is installed.')
            return

    dir_list = os.listdir(os.path.join(dirname, '../data/waves'))
    if (len(dir_list) != 0 and len(dir_list) != 1) or not (len(dir_list) == 1 and dir_list[0] == '.gitkeep'):
        return

    print('Generating WAV files...')
    multi_run(generate, all_chords)

    # Fix 'ø7' filename after generation.
    for _, _, files in os.walk(os.path.join(dirname, '../data/waves/')):
        for file in files:
            if 'm7b5' in file:
                os.rename(os.path.join(dirname, '../data/waves/', file),
                          os.path.join(dirname, '../data/waves/', file.replace('m7b5', 'ø7')))


def wave_feature_generate():
    names = {utils.chroma_cqt: 'cqt', utils.chroma_stft: 'stft', utils.chroma_cens: 'cens',
             utils.chroma_cqtx: 'enhanced_cqt'}
    paths = [os.path.join(dirname, x) for x in ['../data/features/wav_{}.csv'.format(name) for name in names.values()]]
    existence = [os.path.exists(x) for x in paths]
    if all(existence):
        return

    storage = {utils.chroma_cqt: [], utils.chroma_stft: [], utils.chroma_cens: [], utils.chroma_cqtx: []}

    def generate(chord):
        for i in SingleChordContent.inst_table:
            for j in SingleChordContent.play_table.keys():
                p = SingleChordContent(chord, i, j)
                inst = str(p.inst)
                play = str(p.method)
                p = p.pattern
                filename = p.chord.notation + '_' + inst + '_' + play
                wave_name = os.path.join(dirname, '../data/waves/{}.wav'.format(filename))
                notes = [x for x in all_notes if x not in utils.note_alts.keys()]
                extra = {'notation': p.chord.notation, 'root': str(p.chord.root), 'quality': p.chord.quality, 'bass': str(p.chord.bass)}

                duration = librosa.get_duration(filename=wave_name)
                # Cut silent part for generated waves files.
                # Less computation than librosa.effects.trim().
                y, _ = librosa.load(wave_name, duration=duration - 2)
                for method in storage.keys():
                    chroma = utils.means(method(y))
                    chroma = dict(zip(notes, chroma.tolist()))
                    extra['method'] = names[method]
                    storage[method].append({**chroma, **extra})

    print('Extracting features from WAV files...')
    multi_run(generate, all_chords)

    for function, name in names.items():
        try:
            with open(os.path.join(dirname, '../data/features/wav_{}.csv'.format(name)), 'xt', encoding="utf-8",
                      newline='\n') as f:
                pandas.DataFrame(storage[function]).to_csv(f, index=False, line_terminator='\n')
        except FileExistsError:
            pass
        except Exception as e:
            raise e


def noise_feature_generate():
    if os.path.exists(os.path.join(dirname, '../data/features/noise.csv')):
        return

    random.seed(10)
    templates = []
    full = np.full(12, 1)
    while len(templates) < 12:
        r = random.random()
        if r < noise:
            templates.append(full * r)

    data = []
    while len(data) < len(SingleChordContent.inst_table) + len(SingleChordContent.play_table):
        r = random.random()
        if r < noise:
            notes = [x for x in all_notes if x not in utils.note_alts.keys()]
            chroma = dict(zip(notes, templates[random.randrange(len(templates) - 1)] * r))
            extra = {'notation': 'N', 'root': 'N', 'quality': 'N', 'bass': 'N'}
            data.append({**chroma, **extra})

    try:
        with open(os.path.join(dirname, '../data/features/noise.csv'), 'xt', encoding="utf-8", newline='\n') as f:
            print('Generating non-chord features...')
            pandas.DataFrame(data).to_csv(f, index=False, line_terminator='\n')
    except FileExistsError:
        pass
    except Exception as e:
        raise e


def main():
    dir_check()
    basic_generate()
    midi_generate()
    wave_generate()
    wave_feature_generate()
    noise_feature_generate()
    print('Done.')


if __name__ == '__main__':
    main()
