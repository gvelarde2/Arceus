# Agilent 34401A DMM Controller
import asyncio
import time

import matplotlib.pyplot as plt
import pandas as pd
import pyvisa

from arceus.utils.data_directory import DataDirectory

RESOURCE = "GPIB0::4::INSTR"


class A34401A:

    def __init__(self, resource=RESOURCE):
        self.dmm = pyvisa.ResourceManager().open_resource(resource)

    def volt_read_init(self):
        self.dmm.write(":SENSe:FUNCtion 'VOLTage:DC'")

    async def volt_read(self, holdtime, Tset, deviceID, comment=''):
        startTime = time.time()
        timeList = []
        voltList = []

        while (time.time() - startTime) < holdtime:
            self.dmm.write("INITiate")
            volt = float(self.dmm.query(":FETCh?"))
            voltList.append(volt)
            timeList.append(float(time.time()))
            await asyncio.sleep(0.5)

        dt = pd.DataFrame(voltList, timeList)
        dt.to_csv(
            DataDirectory(dID=deviceID, comment=comment).path()
            + 'TimevsVolt_Tset{}.csv'.format(Tset),
            header=False,
        )

    def volt_plot(self, timeList, voltList, show, deviceID):
        fig, ax = plt.subplots()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')
        ax.plot(timeList, voltList)
        if show:
            plt.show()
        fig.savefig(DataDirectory(dID=deviceID).path() + 'TimevsVolt.png')

    def res_read(self, holdtime, deviceID, pt, comment=''):
        if pt == 2:
            self.dmm.write(":SENSe:FUNCtion 'RESistance'")
        elif pt == 4:
            self.dmm.write(":SENSe:FUNCtion 'FRESistance'")
        startTime = time.time()
        timeList = []
        rList = []

        while (time.time() - startTime) < holdtime:
            self.dmm.write("INITiate")
            res = float(self.dmm.query(":FETCh?"))
            rList.append(res)
            timeList.append(float(time.time() - startTime))
            time.sleep(0.5)

        dt = pd.DataFrame(rList, timeList)
        dt.to_csv(
            DataDirectory(dID=deviceID, comment=comment).path() + 'TimevsRes.csv',
            header=False,
        )
        return timeList, rList

    def res_plot(self, timeList, rList, show, deviceID):
        fig, ax = plt.subplots()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Resistance (Ohm)')
        ax.plot(timeList, rList)
        if show:
            plt.show()
        fig.savefig(DataDirectory(dID=deviceID).path() + 'TimevsRes.png')


if __name__ == "__main__":
    dmm = A34401A()
    time_data, res = dmm.res_read(holdtime=5, deviceID=2, pt=4)
