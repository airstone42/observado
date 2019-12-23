#!/usr/bin/env python3
import json

from src.chords import *


def basic_generate():
    # Calculate all chords by combine notes and chord templates
    all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in Note.notes if x not in Note.alt_table.keys()
                  for y in Template.table.keys()]
    data = {'basic': []}
    for i in all_chords:
        t = Template(i)
        if t.available:
            item = {'notation': t.chord.notation, 'array': t.array.tolist(), 'root': str(t.chord.root),
                    'quality': t.chord.quality, 'bass': str(t.chord.bass)}
            data['basic'].append(item)
    try:
        with open('../data/basic.json', 'xt') as f:
            json.dump(data, f)
    except FileExistsError:
        pass
    except Exception as e:
        raise e


def main():
    basic_generate()


if __name__ == '__main__':
    main()
