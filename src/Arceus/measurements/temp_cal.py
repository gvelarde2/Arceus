# Temperature Calibration Measurement
# Sweeps current (K6220) while simultaneously logging temperature (K2110)
# and voltage (A34401A) over a fixed hold time per step.
import asyncio
import time

import numpy as np
import pandas as pd
import pyvisa

from arceus.instruments.keithley_6220 import K6220
from arceus.utils.data_directory import DataDirectory

# Direct VISA handles used for the async logging coroutines
_rm = pyvisa.ResourceManager()
dmm_temp = _rm.open_resource("USB0::0x05E6::0x2110::8020860::INSTR")   # K2110 thermocouple
dmm_volt = _rm.open_resource("GPIB0::4::INSTR")                         # A34401A voltage

dmm_temp.write(":SENSe:FUNCtion 'TCOuple'")
dmm_volt.write(":SENSe:FUNCtion 'VOLTage:DC'")


async def _log_temp(holdtime, Tset, deviceID, comment):
    startTime = time.time()
    timeList, tempList = [], []
    while (time.time() - startTime) < holdtime:
        dmm_temp.write("INITiate")
        tempList.append(float(dmm_temp.query(":FETCh?")))
        timeList.append(float(time.time()))
        await asyncio.sleep(0.5)
    dt = pd.DataFrame(tempList, timeList)
    dt.to_csv(
        DataDirectory(dID=deviceID, comment=comment).path()
        + 'TimevsTemp_TsetC_{}_Iset_{}.csv'.format(Tset, comment),
        header=False,
    )


async def _log_volt(holdtime, Tset, deviceID, comment):
    startTime = time.time()
    timeList, voltList = [], []
    while (time.time() - startTime) < holdtime:
        dmm_volt.write("INITiate")
        voltList.append(float(dmm_volt.query(":FETCh?")))
        timeList.append(float(time.time()))
        await asyncio.sleep(0.5)
    dt = pd.DataFrame(voltList, timeList)
    dt.to_csv(
        DataDirectory(dID=deviceID, comment=comment).path()
        + 'TimevsVolt_TsetC_{}_Iset_{}.csv'.format(Tset, comment),
        header=False,
    )


async def main(rep, setpoint, Istart=None, Istop=None, Iden=None, deviceID=1, holdtime=20):
    """
    Run the temperature calibration sweep.

    Parameters
    ----------
    rep      : 'multi' sweeps Istart→Istop in Iden steps; 'single' uses 100 µA.
    setpoint : Target temperature setpoint label (°C) used in filenames.
    Istart   : Start current for multi-rep sweep (A).
    Istop    : Stop current for multi-rep sweep (A).
    Iden     : Number of current steps for multi-rep sweep.
    deviceID : Device ID passed to DataDirectory.
    holdtime : Seconds to log at each current step.
    """
    Isource = K6220()

    if rep == 'multi':
        arr = np.linspace(Istart, Istop, Iden)
        arr = ["{:0.2e}".format(x) for x in arr]
        for x in arr:
            Isource.curr_on(x)
            await asyncio.gather(
                _log_temp(holdtime, setpoint, deviceID, x),
                _log_volt(holdtime, setpoint, deviceID, x),
            )
    elif rep == 'single':
        x = '100E-6'
        Isource.curr_on(x)
        await asyncio.gather(
            _log_temp(holdtime, setpoint, deviceID, x),
            _log_volt(holdtime, setpoint, deviceID, x),
        )

    Isource.curr_off()


if __name__ == "__main__":
    asyncio.run(main(rep='single', setpoint=30, Istart=50e-6, Istop=500e-6, Iden=10))
