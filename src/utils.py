import numpy as np

note_values = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

note_alts = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

# Chord pattern for C
chord_table = {'M': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
               'm': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]),
               'aug': np.array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]),
               'dim': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]),
               '7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
               'm7': np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0]),
               'maj7': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1]),
               'dim7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0]),
               'ø7': np.array([1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]),
               '9': np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]),
               'add9': np.array([1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
               'add6': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0]),
               'sus2': np.array([1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
               'sus4': np.array([1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]), }

all_notes = sorted(tuple(x for x in (x for x in (x for y in ((chr(x), chr(x) + '#', chr(x) + 'b') for x in
                                                             range(ord('A'), ord('G') + 1)) for x in y)) if
                         x not in ('B#', 'Cb', 'E#', 'Fb')),
                   key=lambda x, v=note_values, t=note_alts: v[x] if x not in t else v[t[x]])

# Calculate all chords by combine notes and chord patterns.
all_chords = [(lambda x, y: x + y if y != 'M' else x)(x, y) for x in all_notes if x not in note_alts.keys() for y in
              chord_table.keys()]
