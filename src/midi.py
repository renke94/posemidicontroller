from rtmidi import MidiMessage, RtMidiOut

class MidiController:
    def __init__(self):
        self.midi_out = RtMidiOut()
        self.midi_out.openVirtualPort("Pose MIDI Controller")

    def __del__(self):
        self.midi_out.closePort()

    def send_cc(self, control: int, value: float):
        m = MidiMessage.controllerEvent(10, control, int(value * 127))
        self.midi_out.sendMessage(m)

def controller_event(control: int, channel: int, value: int):
    return MidiMessage.controllerEvent(channel, control, value)
