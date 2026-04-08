# Keysight E36312A Triple-Output Power Supply Controller
from datetime import datetime

import pyvisa

RESOURCE = 'USB0::0x2A8D::0x1102::MY61007122::INSTR'


class E36312A:

    def __init__(self, resource=RESOURCE):
        self.ps = pyvisa.ResourceManager().open_resource(resource)

    def on(self, voltage, current):
        self.ps.write('SYST:REM\n')
        self.ps.write('APPLY P25V, {}, {}\n'.format(voltage, current))
        self.ps.write('OUTPUT:STATE ON\n')

    def off(self):
        self.ps.write('OUTPUT:STATE OFF\n')
        self.ps.write('*CLS\n')
        self.ps.write('*RST\n')

    @staticmethod
    def timestamp():
        return datetime.today().timestamp()


if __name__ == "__main__":
    ps = E36312A()
    ps.on(1.0, 0.55)
    ps.off()
