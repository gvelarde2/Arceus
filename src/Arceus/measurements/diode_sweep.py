# Diode Heating Sweep
# Steps the power supply through a voltage range to heat the diode,
# then collects I-V curves with the parameter analyzer at each step.
import time

import numpy as np

from arceus.instruments.agilent_4156 import connect as pa_connect, run_sweep
from arceus.instruments.keysight_e36312a import E36312A


def diode_sweep(voltage_steps, current_limit, iterations, smu, cool_t, save_path):
    """
    Heat the diode to each voltage in voltage_steps, collect I-V sweeps,
    then cool before moving to the next step.

    Parameters
    ----------
    voltage_steps  : array-like  Heating voltages (V).
    current_limit  : float       Power supply current limit (A).
    iterations     : int         Number of I-V sweeps per voltage step.
    smu            : Agilent4156 Configured PA instance from agilent_4156.connect().
    cool_t         : float       Cool-down time between steps (s).
    save_path      : str         Root directory for CSV output.
    """
    ps = E36312A()

    for v in voltage_steps:
        ps.on(v, current_limit)
        t0 = ps.timestamp()
        run_sweep(voltage_steps, iterations, t0, smu, save_path)
        ps.off()
        smu = pa_connect()   # re-arm the PA for the next step
        time.sleep(cool_t)


if __name__ == '__main__':
    voltage_steps = np.round(np.linspace(0, 3, 121), 3)
    smu = pa_connect()
    diode_sweep(
        voltage_steps=voltage_steps,
        current_limit=0.55,
        iterations=11,
        smu=smu,
        cool_t=1800,
        save_path='C:\\Lab_Data\\Data\\D00',
    )
