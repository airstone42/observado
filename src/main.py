#!/usr/bin/env python3
import json
import os
from concurrent import futures

from src.chords import *
from src.midi import *

dirname = os.path.dirname(__file__)

# Calculate all chords by combine notes and chord patterns.
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in Note.notes if x not in Note.alt_table.keys()
              for y in Pattern.table.keys()]


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

    with futures.ThreadPoolExecutor(max_workers=12) as pool:
        pool.map(generate, all_chords)


def main():
    basic_generate()
    midi_generate()


if __name__ == '__main__':
    main()
