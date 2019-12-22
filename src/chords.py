import re

import numpy as np


# Capitalize musical notes name.
def note_upper(name: str) -> str:
    try:
        if len(name) > 2:
            raise ValueError
        return name[0].upper() + name[1] if len(name) == 2 else name[0].upper()
    except ValueError as e:
        raise e


class Note(object):
    value_table = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10,
                   'B': 11}

    alt_table = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

    notes = sorted(tuple(x for x in (x for x in
                                     (x for y in
                                      ((chr(x), chr(x) + '#', chr(x) + 'b') for x in range(ord('A'), ord('G') + 1))
                                      for x in y)) if x not in ('B#', 'Cb', 'E#', 'Fb')),
                   key=lambda x, v=value_table, t=alt_table: v[x] if x not in t else v[t[x]])

    def __init__(self, name: str):
        try:
            if not self._check(name):
                raise ValueError
            self._note: str = note_upper(name)
        except ValueError as e:
            raise e

    def __repr__(self):
        return 'Note({})'.format(self._note)

    def __str__(self):
        return '{}'.format(self._note)

    def __eq__(self, other):
        try:
            other = str(other)
            pattern = r'Note\((\w+)\)'
            ivt_table = {v: k for k, v in self.alt_table.items()}
            if re.match(pattern, other):
                other = [x for x in re.split(pattern, other) if x][0]
            other = note_upper(other)
            return True if self._note == other or (
                    self._note in self.alt_table and self.alt_table[self._note] == other) or (
                                   self._note in ivt_table and ivt_table[self._note] == other) else False
        except ValueError:
            return False

    # Check if note name is legal.
    def _check(self, name: str) -> bool:
        return True if note_upper(name) in self.notes else False

    # Get position by note.
    def value(self) -> int:
        note = self.alt_table[self._note] if self._note in self.alt_table else self._note
        return self.value_table[note]


class Chord(object):
    chord_pattern = r'([A-G|a-g][#|b]?)((add6|7|maj7)?sus(2|4)?|((m|aug)?add6)|m?maj7|[m|ø]7?|9|11|13|((aug|dim)?(' \
                    r'7|maj7|add9)?)?)/?([A-G|a-g][#|b]?)?'

    def __init__(self, notation: str):
        try:
            if not re.fullmatch(self.chord_pattern, notation):
                raise ValueError
            groups = [x for x in re.split(self.chord_pattern, notation) if x]
            self.root: Note = Note(groups[0])
            self.quality: str = groups[1] if len(groups) != 1 else 'M'
            self.notation: str = str(self.root) + (self.quality if self.quality != 'M' else '')
            if not re.match(r'.*/.*', notation):
                self.bass: Note = self.root
            else:
                self.bass: Note = Note(groups[-1])
                self.notation += '/' + str(self.bass)
        except ValueError as e:
            raise e

    def __repr__(self):
        return 'Chord({!r})'.format(self.__dict__)

    def __str__(self):
        return 'Chord({})'.format(self.notation)


class Template(object):
    # Chord template for C
    table = {'M': np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]),
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

    def __init__(self, chord):
        try:
            self.array: np.ndarray = np.array([])
            self.chord: Chord = chord if isinstance(chord, Chord) else Chord(chord)
            self.available: bool = False
            if self.chord.quality in self.table and self.chord.root == self.chord.bass:
                self.available = True
                # Transpose by notes.
                self.array = np.roll(self.table[self.chord.quality], self.chord.root.value())
        except ValueError as e:
            raise e

    def __repr__(self):
        return 'Template({!r})'.format(self.__dict__)

    def __str__(self):
        return 'Template({}, {})'.format(str(self.chord), str(self.array))
