# Keithley 6220 Precision Current Source Controller
import time

import pyvisa

RESOURCE = "GPIB0::12::INSTR"


class K6220:

    def __init__(self, resource=RESOURCE):
        self.src = pyvisa.ResourceManager().open_resource(resource)

    def curr_on(self, setpoint):
        self.src.write(":SOUR:CURR:RANG {}".format(setpoint))
        self.src.write(":SOUR:CURR:AMPL {}".format(setpoint))
        self.src.write(":OUTPut:STAT ON")

    def curr_off(self):
        self.src.write(":OUTPut:STAT OFF")


if __name__ == "__main__":
    src = K6220()
    src.curr_on(100e-6)
    time.sleep(5)
    src.curr_off()
