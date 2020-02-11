#!/usr/bin/env python3
import unittest

from observado.chords import *


class ChordTestCase(unittest.TestCase):
    def test_note_upper(self):
        self.assertEqual(Note.upper('Bb'), 'Bb')
        self.assertEqual(Note.upper('c#'), 'C#')
        self.assertEqual(Note.upper('e'), 'E')
        self.assertRaises(ValueError, Note.upper, 'C##')

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
        self.assertIsInstance(Chord('C'), Chord)
        self.assertIsInstance(Chord('Am7'), Chord)
        self.assertIsInstance(Chord('Fmmaj7'), Chord)
        self.assertIsInstance(Chord('Abmaj7sus2'), Chord)
        self.assertIsInstance(Chord('C#dim7/Gb'), Chord)
        self.assertIsInstance(Chord('Bbadd6sus2/Gb'), Chord)
        chord = Chord('Bbmaj7sus4/A')
        self.assertEqual(str(chord), 'Chord(Bbmaj7sus4/A)')
        self.assertEqual(chord.root, Note('Bb'))
        self.assertEqual(chord.bass, Note('A'))
        self.assertEqual(chord.quality, 'maj7sus4')

    def test_patterns(self):
        self.assertRaises(ValueError, Pattern, 'C#/E#')
        self.assertIsInstance(Pattern('Fmmaj7'), Pattern)
        self.assertIsInstance(Pattern(Chord('Abmaj7sus2')), Pattern)
        self.assertFalse(Pattern(Chord('Abmaj7sus2')).available)
        self.assertFalse(Pattern(Chord('Cmaj7/G')).available)
        self.assertTrue(Pattern(Chord('Cmaj7/C')).available)
        p = Pattern(Chord('Cmaj7'))
        self.assertTrue(p.available)
        self.assertEqual(str(p.array), str(np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1])))


if __name__ == '__main__':
    unittest.main()
