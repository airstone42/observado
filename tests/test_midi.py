import unittest

from observado.lib.midi import *


class MIDITestCase(unittest.TestCase):
    def test_pattern(self):
        self.assertRaises(ValueError, MIDIPattern, 'C##')
        self.assertIsInstance(MIDIPattern(Chord('Am7')), MIDIPattern)
        self.assertFalse(MIDIPattern('c/g').available)
        self.assertTrue(MIDIPattern('C').available)

    def test_content(self):
        self.assertRaises(ValueError, SingleChordContent, 'C##')
        self.assertIsInstance(SingleChordContent('Am7'), SingleChordContent)
        self.assertIsInstance(SingleChordContent(Chord('Am7')), SingleChordContent)
        self.assertIsInstance(SingleChordContent(Pattern(Chord('Am7'))), SingleChordContent)
        self.assertIsInstance(SingleChordContent(MIDIPattern(Chord('Am7'))), SingleChordContent)


if __name__ == '__main__':
    unittest.main()
