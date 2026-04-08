# Keysight 33600A-Series Arbitrary Waveform Generator Controller
import pyvisa

from arceus.utils.waveform import wf_settings

RESOURCE = 'USB0::0x0957::0x2C07::MY62003942::INSTR'


class AWG:

    def __init__(self, wf, resource=RESOURCE):
        self.wf = wf
        self.awg = None
        self.aw_data = None

    def connect(self):
        self.awg = pyvisa.ResourceManager().open_resource(self.wf.__class__.__module__)

    def read_awg(self, resource=RESOURCE):
        self.awg = pyvisa.ResourceManager().open_resource(resource)
        import csv
        with open(self.wf.get_path(), 'r') as f:
            reader = csv.reader(f)
            self.aw_data = [float(row[0]) for row in reader]

    def settings(self):
        self.awg.write("*CLS")
        self.awg.write("*RST")
        self.awg.write(':SOURce1:DATA:VOLatile:CLEar')
        self.awg.write(':SOURce1:DATA:ARB:DAC {}, {}'.format('myarbx', ','.join(map(str, self.aw_data))))
        self.awg.write("SOURce1:FUNCtion:ARBitrary myarbx")
        self.awg.write(':SOURce1:DATA:VOLatile:CLEar')
        self.awg.write(':SOURce1:DATA:ARB:DAC {}, {}'.format('myarbx', ','.join(map(str, self.aw_data))))
        self.awg.write("SOURce1:FUNCtion:ARBitrary myarbx")
        self.awg.write(':SOURce1:FUNCtion ARB')
        self.awg.write(':SOURce1:FUNCtion:ARB:SRATe 1e4')
        self.awg.write(':SOURCE1:VOLTage 0.5')
        self.awg.write(':SOURce1:BURSt:MODE TRIGgered')
        self.awg.write(':SOURce1:BURSt:NCYCles 1')
        self.awg.write(':TRIGger:SOURce BUS')
        self.awg.write(':BURSt:STATe ON')
        self.awg.write(':OUTPut1 ON')
        self.awg.write("*OPC?")

    def trigger(self):
        self.awg.write("*TRG")

    def off(self):
        self.awg.write(':OUTPut1 OFF')


if __name__ == "__main__":
    wf = wf_settings(0, 1, 100, 50)
    wf.wf_generator()
    run = AWG(wf)
    run.read_awg()
    run.settings()
