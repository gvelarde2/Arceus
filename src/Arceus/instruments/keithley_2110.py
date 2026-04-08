# Keithley 2110 DMM Controller
import asyncio
import time

import matplotlib.pyplot as plt
import pandas as pd
import pyvisa

from arceus.utils.data_directory import DataDirectory

RESOURCE = "USB0::0x05E6::0x2110::8020860::INSTR"


class K2110:

    def __init__(self, resource=RESOURCE):
        self.dmm = pyvisa.ResourceManager().open_resource(resource)

    def temp_read_init(self):
        self.dmm.write(":SENSe:FUNCtion 'TCOuple'")

    async def temp_read(self, holdtime, Tset, deviceID, comment=''):
        startTime = time.time()
        timeList = []
        tempList = []

        while (time.time() - startTime) < holdtime:
            self.dmm.write("INITiate")
            temp = float(self.dmm.query(":FETCh?"))
            tempList.append(temp)
            timeList.append(float(time.time()))
            await asyncio.sleep(0.5)

        dt = pd.DataFrame(tempList, timeList)
        dt.to_csv(
            DataDirectory(dID=deviceID, comment=comment).path()
            + 'TimevsTemp_Tset{}C.csv'.format(Tset),
            header=False,
        )

    def temp_plot(self, timeList, tempList, show, Tset, deviceID):
        fig, ax = plt.subplots()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Temperature (C)')
        ax.plot(timeList, tempList)
        if show:
            plt.show()
        fig.savefig(
            DataDirectory(dID=deviceID).path()
            + 'TimevsTemp_Tset{}C.png'.format(Tset)
        )


if __name__ == "__main__":
    dmm = K2110()
    dmm.temp_read_init()
    asyncio.run(dmm.temp_read(holdtime=5, Tset=25, deviceID=1))
