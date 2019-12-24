from src.chords import *


class MIDIPattern(Pattern):
    # MIDI note numbers of C3 to B3, C4 to B4, C5 to B5
    bass = [x for x in range(48, 59 + 1)]
    alto = [x for x in range(60, 71 + 1)]
    treble = [x for x in range(72, 83 + 1)]

    def __init__(self, chord):
        super().__init__(chord)
        self.component: list = self._calculate()

    def _calculate(self) -> list:
        bass = [self.bass[self.chord.bass.value()]]
        # Pick notes by matching array.
        alto = [self.alto[x] for x in range(len(self.array)) if self.array[x]]
        treble = [self.treble[self.chord.bass.value()]]
        return sorted(bass + alto + treble, reverse=True)

    def __repr__(self):
        return 'MIDIPattern({!r})'.format(self.__dict__)

    def __str__(self):
        return 'MIDIPattern({}, {})'.format(str(self.chord), str(self.component))
