#!/usr/bin/env python3
"""Convert a Windsong Lyre markdown chart to MIDI.

Only uses the Python standard library and mido.
"""

import argparse
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import mido

# Same mapping as lyre.py
KEYS = 'ZXCVBNMASDFGHJQWERTYU'
WHITE = (0, 2, 4, 5, 7, 9, 11)
LOWEST = 48
HIGHEST = 83
KEY_OF = {LOWEST + 12 * (i // 7) + WHITE[i % 7]: k for i, k in enumerate(KEYS)}
PITCH_OF = {k: p for p, k in KEY_OF.items()}

TPB = 480
PROGRAM = 46          # General MIDI orchestral harp
DEFAULT_DURATION = TPB  # one quarter note for taps without explicit release

HEADER_RE = re.compile(r'^([\d.]+)\s*BPM,\s*(\d+)/(\d+)', re.M)
CODE_RE = re.compile(r'```\n(.*?)\n```', re.S)
SLOT_RE = re.compile(r'(<[^>]+>)?(\([A-Za-z]+\)|[A-Za-z]| )')


TRANSPOSE_RE = re.compile(r'transposed\s+([+-]\d+)\s+semitones')
KEY_CHANGE_RE = re.compile(r'([+-]\d+)\s+from\s+bar\s+(\d+)\s+beat\s+(\d+)')


def parse_md(text: str):
    """Parse the markdown chart.

    The header lists the transposition of each passage, such as
    'transposed +5 semitones, +4 from bar 9 beat 1'. Each pitch is shifted back by the
    transposition in force at its press, so the notes come out in the original key.

    Returns:
        bpm, numerator, denominator, tempo_events, note_events
    """
    m = HEADER_RE.search(text)
    if not m:
        raise ValueError('cannot find header BPM and time signature')
    bpm = float(m.group(1))
    numerator = int(m.group(2))
    denominator = int(m.group(3))

    code_m = CODE_RE.search(text)
    if not code_m:
        raise ValueError('cannot find fenced code block')
    code = code_m.group(1)

    # beat_ticks: ticks of one beat in the chart's time signature.
    # In lyre.py a beat is tpb * 4 / denominator.
    beat_ticks = Fraction(TPB * 4, denominator)
    current_tick = Fraction(0)

    # Absolute transpositions in beats, from the original song, from the header line. The
    # first entry is the starting shift and the rest are the changes listed after it.
    line_end = text.find('\n', m.start())
    header = text[m.start():] if line_end == -1 else text[m.start():line_end]
    transposes = [(0, 0)]
    if t_m := TRANSPOSE_RE.search(header):
        transposes = [(0, int(t_m.group(1)))]
        transposes += [
            ((int(bar) - 1) * numerator + int(beat) - 1, int(shift))
            for shift, bar, beat in KEY_CHANGE_RE.findall(header)
        ]

    def shift_at(beat: int) -> int:
        shift = transposes[0][1]
        for at, value in transposes[1:]:
            if at > beat:
                break
            shift = value
        return shift

    tempo_events = []   # (tick, tempo_us)
    note_events = []    # (tick, 'on'/'off', pitch in the original key)
    held = {}           # key letter -> transposition of its latest press

    for line in code.splitlines():
        if not line.strip():
            continue

        # Each line is a sequence of beats, each ending with '/'.
        beats = line.split('/')
        if beats and beats[-1] == '':
            beats.pop()

        for beat in beats:
            slots = list(SLOT_RE.finditer(beat))
            n = len(slots)
            if n == 0:
                continue

            slot_ticks = beat_ticks / n

            for slot in slots:
                tick = round(current_tick)
                beat_index = tick // beat_ticks
                marker = slot.group(1)   # e.g. "<120>"
                token = slot.group(2)    # e.g. "C", "c", "(ZC)", " "

                if marker:
                    bpm_val = float(marker[1:-1])
                    tempo_events.append((tick, mido.bpm2tempo(bpm_val)))

                # A release takes the shift of its press, so a key held across a key change
                # keeps one pitch and still pairs with its press.
                if token == ' ':
                    pass
                elif token.startswith('('):
                    # Simultaneous events. Uppercase = press, lowercase = release.
                    for ch in token[1:-1]:
                        if ch.isupper():
                            note_events.append((tick, 'on', PITCH_OF[ch] - shift_at(beat_index)))
                            held[ch] = shift_at(beat_index)
                        elif ch.islower():
                            up = ch.upper()
                            note_events.append(
                                (tick, 'off', PITCH_OF[up] - held.pop(up, shift_at(beat_index)))
                            )
                else:
                    ch = token
                    if ch.isupper():
                        note_events.append((tick, 'on', PITCH_OF[ch] - shift_at(beat_index)))
                        held[ch] = shift_at(beat_index)
                    elif ch.islower():
                        up = ch.upper()
                        note_events.append(
                            (tick, 'off', PITCH_OF[up] - held.pop(up, shift_at(beat_index)))
                        )

                current_tick += slot_ticks

    return bpm, numerator, denominator, tempo_events, note_events


def build_midi(
    bpm,
    numerator,
    denominator,
    tempo_events,
    note_events,
    program=PROGRAM,
    default_duration=DEFAULT_DURATION,
):
    midi_events = []

    initial_tempo = mido.bpm2tempo(bpm)
    midi_events.append((0, 0, mido.MetaMessage('set_tempo', tempo=initial_tempo)))
    midi_events.append(
        (0, 0, mido.MetaMessage('time_signature', numerator=numerator, denominator=denominator))
    )
    midi_events.append((0, 1, mido.Message('program_change', program=program, channel=0)))

    for tick, tempo in tempo_events:
        midi_events.append((tick, 0, mido.MetaMessage('set_tempo', tempo=tempo)))

    # Group note on/off by pitch.
    by_pitch = defaultdict(list)
    for tick, typ, pitch in note_events:
        by_pitch[pitch].append((tick, typ))

    for pitch, evs in by_pitch.items():
        # At the same tick, handle note_off before note_on.
        evs.sort(key=lambda x: (x[0], 0 if x[1] == 'off' else 1))
        active_start = None

        for tick, typ in evs:
            if typ == 'on':
                if active_start is not None:
                    end = min(active_start + default_duration, tick)
                    midi_events.append(
                        (active_start, 3, mido.Message('note_on', note=pitch, velocity=80, channel=0))
                    )
                    midi_events.append(
                        (end, 2, mido.Message('note_off', note=pitch, velocity=0, channel=0))
                    )
                active_start = tick
            else:  # off
                if active_start is not None:
                    midi_events.append(
                        (active_start, 3, mido.Message('note_on', note=pitch, velocity=80, channel=0))
                    )
                    midi_events.append(
                        (tick, 2, mido.Message('note_off', note=pitch, velocity=0, channel=0))
                    )
                    active_start = None

        if active_start is not None:
            end = active_start + default_duration
            midi_events.append(
                (active_start, 3, mido.Message('note_on', note=pitch, velocity=80, channel=0))
            )
            midi_events.append(
                (end, 2, mido.Message('note_off', note=pitch, velocity=0, channel=0))
            )

    # Priority at the same tick:
    # 0 meta, 1 program change, 2 note_off, 3 note_on
    midi_events.sort(key=lambda x: (x[0], x[1]))

    midi = mido.MidiFile(ticks_per_beat=TPB)
    track = mido.MidiTrack()
    now = 0
    for tick, _, msg in midi_events:
        msg.time = tick - now
        track.append(msg)
        now = tick

    midi.tracks.append(track)
    return midi


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='lyre markdown chart')
    parser.add_argument('-o', '--output', type=Path, help='output MIDI path')
    parser.add_argument(
        '--program', type=int, default=PROGRAM,
        help='MIDI program number (default: 46, orchestral harp)'
    )
    parser.add_argument(
        '--default-duration', type=int, default=DEFAULT_DURATION,
        help='ticks for notes without explicit release (default: 480)'
    )
    args = parser.parse_args()

    text = args.source.read_text(encoding='utf-8')
    bpm, numerator, denominator, tempo_events, note_events = parse_md(text)

    midi = build_midi(
        bpm,
        numerator,
        denominator,
        tempo_events,
        note_events,
        program=args.program,
        default_duration=args.default_duration,
    )

    output = args.output or args.source.with_suffix('.mid')
    midi.save(output)
    print(output)


if __name__ == '__main__':
    main()