# Live Temperature Monitor
# Reads voltage from the Agilent 34401A and converts to °C using the
# calibration curve derived during temp_cal. Runs until KeyboardInterrupt,
# then saves the time-vs-temperature trace to a CSV.
import time

import pandas as pd
import pyvisa

from arceus.utils.data_directory import DataDirectory

# Calibration coefficients from temp_cal (single TTC)
CAL_INTERCEPT = 0.72    # V
CAL_SLOPE = -0.0020243  # V/°C

RESOURCE = "GPIB0::4::INSTR"


class LiveTempReader:

    def __init__(self, resource=RESOURCE):
        self.dmm = pyvisa.ResourceManager().open_resource(resource)
        self.dmm.write(":SENSe:FUNCtion 'VOLTage:DC'")

    def run(self, deviceID=0, comment='live'):
        startTime = time.time()
        timeList, voltList, tempList = [], [], []
        try:
            while True:
                self.dmm.write("INITiate")
                volt = float(self.dmm.query(":FETCh?"))
                temp = (volt - CAL_INTERCEPT) / CAL_SLOPE
                t = float(time.time() - startTime)
                timeList.append(t)
                voltList.append(volt)
                tempList.append(temp)
                print(f't={t:.1f}s  T={temp:.2f}°C  V={volt:.5f}V')
        except KeyboardInterrupt:
            print(f'\nStopped. {len(timeList)} samples collected.')
            dt = pd.DataFrame({'time_s': timeList, 'voltage_V': voltList, 'temp_C': tempList})
            path = DataDirectory(dID=deviceID, comment=comment).path()
            fname = path + 'live_temp_trace.csv'
            dt.to_csv(fname, index=False)
            print(f'Saved: {fname}')


if __name__ == "__main__":
    reader = LiveTempReader()
    reader.run(deviceID=0, comment='live')
