#!/usr/bin/env python3
import json

from src.chords import *


def basic_generate():
    # Calculate all chords by combine notes and chord patterns.
    all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in Note.notes if x not in Note.alt_table.keys()
                  for y in Pattern.table.keys()]
    data = {'basic': []}
    for i in all_chords:
        p = Pattern(i)
        if p.available:
            item = {'notation': p.chord.notation, 'array': p.array.tolist(), 'root': str(p.chord.root),
                    'quality': p.chord.quality, 'bass': str(p.chord.bass)}
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
