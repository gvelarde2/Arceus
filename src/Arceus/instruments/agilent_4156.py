# Agilent 4156 Semiconductor Parameter Analyzer Controller
#
# NOTE: PA_Controller.py was missing from the repository. This module
# reconstructs its role based on call signatures found in diode_sweep.py.
# Review and adjust smu.measure() / smu.get_data() calls to match the
# exact pymeasure Agilent4156 API used in your lab setup.

import os
from datetime import datetime

import pandas as pd
from pymeasure.instruments.agilent import Agilent4156

RESOURCE = "GPIB0::2::INSTR"
DEFAULT_CONFIG = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', '..', 'config', 'config_diode.json'
)


def connect(config_path=DEFAULT_CONFIG):
    """Instantiate and configure the parameter analyzer. Returns the smu object."""
    smu = Agilent4156(RESOURCE, read_termination='\n', write_termination='\n', timeout=None)
    smu.reset()
    smu.vsu1.disable
    smu.vsu2.disable
    smu.vmu1.disable
    smu.vmu2.disable
    smu.analyzer_mode = "SWEEP"
    smu.configure(config_path)
    return smu


def run_sweep(voltage_steps, iterations, t0, smu, save_path):
    """
    Run I-V sweeps for each voltage step, repeated `iterations` times.

    Parameters
    ----------
    voltage_steps : array-like
        Voltage values already applied by the power supply (used for labelling).
    iterations : int
        Number of I-V sweeps to collect per voltage step.
    t0 : float
        Unix timestamp marking the start of the heating phase (for file naming).
    smu : Agilent4156
        Configured parameter analyzer instance returned by connect().
    save_path : str
        Directory where CSV results are written.
    """
    os.makedirs(save_path, exist_ok=True)
    timestamp = datetime.fromtimestamp(t0).strftime("%Y%m%d_%H%M%S")

    for i in range(iterations):
        # TODO: replace with the actual pymeasure measurement call for your config
        smu.measure()
        data = smu.get_data()
        df = pd.DataFrame(data)
        fname = os.path.join(save_path, f'IV_iter{i:03d}_{timestamp}.csv')
        df.to_csv(fname, index=False)
        print(f'  Saved sweep {i+1}/{iterations}: {fname}')


if __name__ == "__main__":
    smu = connect()
    run_sweep(
        voltage_steps=[1.0, 1.5, 2.0],
        iterations=3,
        t0=datetime.today().timestamp(),
        smu=smu,
        save_path='C:\\Lab_Data\\Data\\test_sweep',
    )
