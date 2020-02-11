import re

import numpy as np

from observado import utils


class Note(object):
    value_table = utils.note_values

    alt_table = utils.note_alts

    notes = utils.all_notes

    # Capitalize musical notes name.
    @staticmethod
    def upper(name: str) -> str:
        try:
            if len(name) > 2:
                raise ValueError
            return name[0].upper() + name[1] if len(name) == 2 else name[0].upper()
        except ValueError as e:
            raise e

    def __init__(self, name: str):
        try:
            if not self._check(name):
                raise ValueError
            self._note: str = self.upper(name)
        except ValueError as e:
            raise e

    def __hash__(self):
        return hash(str(self))

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
            other = self.upper(other)
            return True if self._note == other or (
                    self._note in self.alt_table and self.alt_table[self._note] == other) or (
                                   self._note in ivt_table and ivt_table[self._note] == other) else False
        except ValueError:
            return False

    # Check if note name is legal.
    def _check(self, name: str) -> bool:
        return True if self.upper(name) in self.notes else False

    # Get position by note.
    def value(self) -> int:
        note = self.alt_table[self._note] if self._note in self.alt_table else self._note
        return self.value_table[note]


class Chord(object):
    pattern = r'([A-G|a-g][#|b]?)((add6|7|maj7)?sus(2|4)?|((m|aug)?add6)|m?maj7|[m|ø]7?|9|11|13|((aug|dim)?(' \
              r'7|maj7|add9)?)?)/?([A-G|a-g][#|b]?)?'

    def __init__(self, notation: str):
        try:
            if not re.fullmatch(self.pattern, notation):
                raise ValueError
            groups = [x for x in re.split(self.pattern, notation) if x]
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


class Pattern(object):
    table = utils.chord_table

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
        return 'Pattern({!r})'.format(self.__dict__)

    def __str__(self):
        return 'Pattern({}, {})'.format(str(self.chord), str(self.array))
