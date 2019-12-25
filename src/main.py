#!/usr/bin/env python3
import json
import os
import subprocess
from concurrent import futures

from src.chords import *
from src.midi import *

dirname = os.path.dirname(__file__)

# Calculate all chords by combine notes and chord patterns.
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in Note.notes if x not in Note.alt_table.keys()
              for y in Pattern.table.keys()]


def dir_check():
    def check_and_make(subdir):
        if not os.path.exists(os.path.join(dirname, subdir)):
            os.mkdir(os.path.join(dirname, subdir))

    print('Checking directories...')
    for i in ['../data', '../data/midi', '../data/wave']:
        check_and_make(i)


def basic_generate():
    data = {'basic': []}
    for i in all_chords:
        p = Pattern(i)
        if p.available:
            item = {'notation': p.chord.notation, 'array': p.array.tolist(), 'root': str(p.chord.root),
                    'quality': p.chord.quality, 'bass': str(p.chord.bass)}
            data['basic'].append(item)
    try:
        with open(os.path.join(dirname, '../data/basic.json'), 'xt') as f:
            print('Generating basic patterns...')
            json.dump(data, f)
    except FileExistsError:
        pass
    except Exception as e:
        raise e


def midi_generate():
    def generate(chord):
        for i in MIDIContent.inst_table:
            p = MIDIContent(chord, i)
            filename = p.pattern.chord.notation + '_' + p.inst
            p.write(os.path.join(dirname, '../data/midi/{}.mid'.format(filename)))

    print('Generating MIDI files...')
    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        pool.map(generate, all_chords)


def wave_generate():
    def generate(chord, child):
        for i in MIDIContent.inst_table:
            p = MIDIContent(chord, i)
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
        pool.map(generate, all_chords, child)

    # Fix 'ø7' filename after generation.
    for _, _, files in os.walk(os.path.join(dirname, '../data/wave/')):
        for file in files:
            if 'm7b5' in file:
                os.rename(os.path.join(dirname, '../data/wave/', file),
                          os.path.join(dirname, '../data/wave/', file.replace('m7b5', 'ø7')))


def main():
    dir_check()
    basic_generate()
    midi_generate()
    wave_generate()
    print('Done.')


if __name__ == '__main__':
    main()
