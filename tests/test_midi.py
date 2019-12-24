import unittest

from src.midi import *


class MIDITestCase(unittest.TestCase):
    def test_pattern(self):
        self.assertRaises(ValueError, MIDIPattern, 'C##')
        self.assertIsInstance(MIDIPattern(Chord('Am7')), MIDIPattern)
        self.assertFalse(MIDIPattern('c/g').available)
        self.assertTrue(MIDIPattern('C').available)

    def test_content(self):
        self.assertRaises(ValueError, MIDIContent, 'C##')
        self.assertIsInstance(MIDIContent('Am7'), MIDIContent)
        self.assertIsInstance(MIDIContent(Chord('Am7')), MIDIContent)
        self.assertIsInstance(MIDIContent(Pattern(Chord('Am7'))), MIDIContent)
        self.assertIsInstance(MIDIContent(MIDIPattern(Chord('Am7'))), MIDIContent)


if __name__ == '__main__':
    unittest.main()
