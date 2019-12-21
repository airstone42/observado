#!/usr/bin/env python3
import unittest

from src.chords import *


class ChordTestCase(unittest.TestCase):
    def test_note_upper(self):
        self.assertEqual(note_upper('Bb'), 'Bb')
        self.assertEqual(note_upper('c#'), 'C#')
        self.assertEqual(note_upper('e'), 'E')
        self.assertRaises(ValueError, note_upper, 'C##')

    def test_notes(self):
        self.assertRaises(ValueError, Note, 'C##')
        self.assertRaises(ValueError, Note, 'e#')
        self.assertEqual(str(Note('bb')), 'Bb')
        self.assertEqual(repr(Note('bb')), 'Note(Bb)')
        self.assertEqual(Note('bb').value(), 10)
        self.assertEqual(Note('C').value(), 0)
        self.assertEqual(Note('B'), 'b')
        self.assertNotEqual(Note('a#'), 'C#')
        self.assertEqual(Note('C#'), Note('Db'))
        self.assertEqual(Note('Db'), 'c#')

    def test_chords(self):
        self.assertRaises(ValueError, Chord, 'C##')
        self.assertRaises(ValueError, Chord, 'C#/E#')
        self.assertIsInstance(Chord('Fmmaj7'), Chord)
        self.assertIsInstance(Chord('Abmaj7sus2'), Chord)
        self.assertIsInstance(Chord('C#dim7/Gb'), Chord)
        self.assertIsInstance(Chord('Bbadd6sus2/Gb'), Chord)
        chord = Chord('Bbmaj7sus4/A')
        self.assertEqual(str(chord), 'Chord(Bbmaj7sus4/A)')
        self.assertEqual(chord.root, Note('Bb'))
        self.assertEqual(chord.bass, Note('A'))
        self.assertEqual(chord.quality, 'maj7sus4')


if __name__ == '__main__':
    unittest.main()
