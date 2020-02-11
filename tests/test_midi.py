import unittest

from observado.lib.midi import *


class MIDITestCase(unittest.TestCase):
    def test_pattern(self):
        self.assertRaises(ValueError, MIDI, 'C##')
        self.assertIsInstance(MIDI(Chord('Am7')), MIDI)
        self.assertFalse(MIDI('c/g').available)
        self.assertTrue(MIDI('C').available)

    def test_content(self):
        self.assertRaises(ValueError, MIDIChord, 'C##')
        self.assertIsInstance(MIDIChord('Am7'), MIDIChord)
        self.assertIsInstance(MIDIChord(Chord('Am7')), MIDIChord)
        self.assertIsInstance(MIDIChord(Pattern(Chord('Am7'))), MIDIChord)
        self.assertIsInstance(MIDIChord(MIDI(Chord('Am7'))), MIDIChord)


if __name__ == '__main__':
    unittest.main()
