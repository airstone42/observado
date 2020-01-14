#!/usr/bin/env python3
import os
import subprocess
import threading
from concurrent import futures

import pandas

from src import utils
from src.midi import *

dirname = os.path.dirname(__file__)
all_notes = utils.all_notes
all_chords = utils.all_chords


def dir_check():
    def check_and_make(subdir):
        if not os.path.exists(os.path.join(dirname, subdir)):
            os.mkdir(os.path.join(dirname, subdir))

    print('Checking directories...')
    for i in ['../data', '../data/midi', '../data/wave', '../data/feature']:
        check_and_make(i)


def basic_generate():
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
        with open(os.path.join(dirname, '../data/feature/basic.csv'), 'xt', encoding="utf-8", newline='\n') as f:
            print('Generating basic patterns...')
            pandas.DataFrame(data).to_csv(f, index=False, line_terminator='\n')
    except FileExistsError:
        pass
    except Exception as e:
        raise e


def midi_generate():
    def generate(chord):
        for i in SingleChordContent.inst_table:
            p = SingleChordContent(chord, i)
            filename = p.pattern.chord.notation + '_' + p.inst
            p.write(os.path.join(dirname, '../data/midi/{}.mid'.format(filename)))

    print('Generating MIDI files...')
    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        pool.map(generate, all_chords)


def wave_generate():
    def generate(chord):
        for i in SingleChordContent.inst_table:
            p = SingleChordContent(chord, i)
            filename = p.pattern.chord.notation + '_' + p.inst
            midi_name = os.path.join(dirname, '../data/midi/{}.mid'.format(filename))
            wave_name = os.path.join(dirname, '../data/wave/{}.wav'.format(filename))
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

    print('Generating WAV files...')
    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        pool.map(generate, all_chords)

    # Fix 'ø7' filename after generation.
    for _, _, files in os.walk(os.path.join(dirname, '../data/wave/')):
        for file in files:
            if 'm7b5' in file:
                os.rename(os.path.join(dirname, '../data/wave/', file),
                          os.path.join(dirname, '../data/wave/', file.replace('m7b5', 'ø7')))


def wave_feature_generate():
    storage = {utils.chroma_cqt: [], utils.chroma_stft: [], utils.chroma_cens: [], utils.chroma_cqtx: []}
    names = {utils.chroma_cqt: 'cqt', utils.chroma_stft: 'stft', utils.chroma_cens: 'cens',
             utils.chroma_cqtx: 'enhanced_cqt'}
    lock = threading.Lock()

    def generate(chord):
        for i in SingleChordContent.inst_table:
            p = SingleChordContent(chord, i)
            inst = p.inst
            p = p.pattern
            filename = p.chord.notation + '_' + inst
            wave_name = os.path.join(dirname, '../data/wave/{}.wav'.format(filename))
            notes = [x for x in all_notes if x not in utils.note_alts.keys()]
            extra = {'notation': p.chord.notation, 'root': str(p.chord.root), 'quality': p.chord.quality,
                     'bass': str(p.chord.bass), 'instrument': inst}

            y = utils.load(wave_name)
            for method in storage.keys():
                chroma = utils.means(method(y))
                chroma = dict(zip(notes, chroma.tolist()))
                extra['method'] = names[method]
                with lock:
                    storage[method].append({**chroma, **extra})

    print('Extracting features from WAV files...')
    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        pool.map(generate, all_chords)

    for function, name in names.items():
        try:
            with open(os.path.join(dirname, '../data/feature/wav_{}.csv'.format(name)), 'xt', encoding="utf-8",
                      newline='\n') as f:
                pandas.DataFrame(storage[function]).to_csv(f, index=False, line_terminator='\n')
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
    print('Done.')


if __name__ == '__main__':
    main()
