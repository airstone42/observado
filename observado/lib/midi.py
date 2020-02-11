from observado.lib.chords import Chord, Pattern


# Pattern of MIDI files
class MIDI(Pattern):
    # MIDI note numbers of C3 to B3, C4 to B4
    bass = [x for x in range(48, 59 + 1)]
    alto = [x for x in range(60, 71 + 1)]

    def __init__(self, chord):
        super().__init__(chord)
        self.component: list = self._calc()

    def __repr__(self):
        return 'MIDIPattern({!r})'.format(self.__dict__)

    def __str__(self):
        return 'MIDIPattern({}, {})'.format(str(self.chord), str(self.component))

    def _calc(self) -> list:
        bass = [self.bass[self.chord.bass.value()]]
        # Pick notes by matching array.
        alto = [self.alto[x] for x in range(len(self.array)) if self.array[x]]
        return sorted(bass + alto)


# For generating chord sounds for several seconds with different instruments.
class MIDIChord(object):
    # MIDI header, <'Mthd'><length><format><number of tracks><division>
    _MThd: str = '4d 54 68 64 00 00 00 06 00 01 00 01 00 80'
    # MIDI track type
    _MTrk_type: str = '4d 54 72 6b'
    # MIDI instruments
    inst_table = [0, 1, 2, 10, 12, 24, 25, 26, 27, 40, 41, 42, 48, 49, 54, 55, 56, 57, 80, 81, 88, 89, 90]

    def _play_0(self) -> str:
        # Press keys
        event = ''.join(x for x in ['90' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
        event = event[:event.rfind('00')] + '8400'
        # Release keys
        event += ''.join(x for x in ['80' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
        return event

    def _play_1(self) -> str:
        # Press keys
        event = ''.join(x for x in ['90' + '{:02x}'.format(x) + '408200' for x in self.pattern.component])
        # Release keys
        event += ''.join(x for x in ['80' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
        return event

    def _play_2(self) -> str:
        # Press keys
        event = ''.join(x for x in ['90' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
        event = event[:event.rfind('00')] + '8200'
        # Release keys
        event += ''.join(x for x in ['80' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])

        for i in range(2):
            event += ''.join(x for x in ['90' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
            event = event[:event.rfind('00')] + '8100'
            event += ''.join(x for x in ['80' + '{:02x}'.format(x) + '4000' for x in self.pattern.component])
        return event

    def _play_3(self) -> str:
        # Press keys
        p = ''.join(x for x in ['90' + '{:02x}'.format(x) + '4000' for x in self.pattern.component[1:]])
        event = p + '90' + '{:02x}'.format(self.pattern.component[0]) + '408100'
        # Release keys
        r = ''.join(x for x in ['80' + '{:02x}'.format(x) + '4000' for x in self.pattern.component[1:]])
        r = r[:r.rfind('00')] + '8100'
        event += r
        event += p
        event = event[:event.rfind('00')] + '8100'
        event += r
        event += '80' + '{:02x}'.format(self.pattern.component[0]) + '4000'
        return event

    # chord playing patterns
    play_table = {0: _play_0, 1: _play_1, 2: _play_2, 3: _play_3}

    def __init__(self, pattern, instrument=0, method=0):
        try:
            if isinstance(pattern, str):
                pattern = MIDI(pattern)
            elif isinstance(pattern, Chord):
                pattern = MIDI(pattern)
            elif isinstance(pattern, Pattern) and not isinstance(pattern, MIDI):
                pattern = MIDI(pattern.chord)
            elif not isinstance(pattern, MIDI):
                raise ValueError
            self.pattern: MIDI = pattern
            if instrument in self.inst_table:
                self.inst = instrument
            if method in self.play_table.keys():
                self.method = method
            else:
                raise ValueError
        except ValueError as e:
            raise e

    def __repr__(self):
        return 'MIDIContent({!r})'.format(self.__dict__)

    def __str__(self):
        return 'MIDIPattern({}, {}, {})'.format(str(self.pattern), self.inst, self.method)

    def _content(self) -> bytes:
        return bytes.fromhex(self._head() + self._track())

    def _head(self) -> str:
        return self._MThd

    def _track(self) -> str:
        instrument = 'c0' + '{:02x}'.format(self.inst) + '00'
        # 120 bpm
        tempo = 'ff 51 03 07 A1 20 00'
        event = self.play_table[self.method](self)
        end = 'ff 2f 00'

        data = instrument + tempo + event + end
        thead = self._MTrk_type + '{:08x}'.format(len(bytes.fromhex(data)) + 1) + '00'
        return thead + data

    def write(self, filename: str):
        with open(filename, 'xb') as f:
            f.write(self._content())
