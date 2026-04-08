# Rigol MSO5074 Oscilloscope Controller
from datetime import datetime

import matplotlib.pyplot as plt
import numpy
import pyvisa

RESOURCE = 'USB0::0x1AB1::0x0515::MS5A255207443::INSTR'


class MSO5074:

    def __init__(self, channel, resource=RESOURCE):
        self.scope = pyvisa.ResourceManager().open_resource(resource)
        self.channel = channel

    def set(self):
        self.scope.write("TIMebase:MAIN:SCALe 0.130")
        if self.channel == 1:
            self.scope.write(f":CHANnel{self.channel}:SCALe 2.0")
        else:
            self.scope.write(f":CHANnel{self.channel}:SCALe 0.15")
        self.scope.write(":TRIGger:SWEep SINGle")
        self.scope.write(":TRIGger:EDGE:LEVel 1")

    def set_trig(self):
        self.scope.write(":TRIGger:SWEep SINGle")

    def opc(self):
        return self.scope.write("*OPC?")

    def export(self):
        self.scope.write(f":WAV:SOUR CHAN{self.channel}")
        self.scope.write(f":WAV:DATA? CHAN{self.channel}")
        rawdata = self.scope.read_raw()
        rawdata = rawdata[10:]
        data = numpy.frombuffer(rawdata, 'B')
        plt.plot(data)
        plt.show()
        dt = datetime.today().timestamp()
        print(f'Data saved: {dt}')
        return data


if __name__ == "__main__":
    scope = MSO5074(channel=2)
    scope.set()
    scope.export()
