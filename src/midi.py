from src.chords import Chord, Pattern


class MIDIPattern(Pattern):
    # MIDI note numbers of C3 to B3, C4 to B4
    bass = [x for x in range(48, 59 + 1)]
    alto = [x for x in range(60, 71 + 1)]

    def __init__(self, chord):
        super().__init__(chord)
        self.component: list = self._calculate()

    def _calculate(self) -> list:
        bass = [self.bass[self.chord.bass.value()]]
        # Pick notes by matching array.
        alto = [self.alto[x] for x in range(len(self.array)) if self.array[x]]
        return sorted(bass + alto, reverse=True)

    def __repr__(self):
        return 'MIDIPattern({!r})'.format(self.__dict__)

    def __str__(self):
        return 'MIDIPattern({}, {})'.format(str(self.chord), str(self.component))


# For generating chord sounds for several seconds with different instruments.
class MIDIContent(object):
    # MIDI header, <'Mthd'><length><format><number of tracks><division>
    _MThd: str = '4d 54 68 64 00 00 00 06 00 01 00 01 00 80'

    # MIDI track type
    _MTrk_type: str = '4d 54 72 6b'

    # MIDI instruments map including grand piano, steel guitar, ensemble strings, syn choir, square wave and saw wave.
    inst_table = {'pf': 0, 'gtr': 25, 'str': 48, 'ch': 54, 'sqr': 80, 'saw': 81}

    def __init__(self, pattern, instrument='pf'):
        try:
            if isinstance(pattern, str):
                pattern = MIDIPattern(pattern)
            elif isinstance(pattern, Chord):
                pattern = MIDIPattern(pattern)
            elif isinstance(pattern, Pattern) and not isinstance(pattern, MIDIPattern):
                pattern = MIDIPattern(pattern.chord)
            elif not isinstance(pattern, MIDIPattern):
                raise ValueError
            self.pattern: MIDIPattern = pattern
            if instrument in self.inst_table.keys():
                self.inst = instrument
            else:
                raise ValueError
        except ValueError as e:
            raise e

    def __repr__(self):
        return 'MIDIContent({!r})'.format(self.__dict__)

    def __str__(self):
        return 'MIDIPattern({}, {})'.format(str(self.pattern), self.inst)

    def _content(self) -> bytes:
        return bytes.fromhex(self._head() + self._track())

    def _head(self) -> str:
        return self._MThd

    def _track(self) -> str:
        instrument = 'c0' + '{:02x}'.format(self.inst_table[self.inst]) + '00'

        # Press keys
        event = ''.join(x for x in ['90' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
        event = event[:event.rfind('00')] + '8800'
        # Release keys
        event += ''.join(x for x in ['80' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])

        end = 'ff 2f 00'

        data = instrument + event + end
        thead = self._MTrk_type + '{:08x}'.format(len(bytes.fromhex(data)) + 1) + '00'
        return thead + data

    def write(self, filename: str):
        with open(filename, 'xb') as f:
            f.write(self._content())
