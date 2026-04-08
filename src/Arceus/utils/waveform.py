# Arbitrary Waveform Generator — ramped pulse-train waveform builder
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class wf_settings:
    """
    Build a ramped pulse-train arbitrary waveform and save it as a CSV
    compatible with the Keysight 33600A DAC format.

    Parameters
    ----------
    startV : float   Starting voltage of the ramp.
    endV   : float   Ending voltage of the ramp.
    v_steps: int     Number of voltage steps across the ramp.
    duty   : int     Duty cycle (0–100). ON samples per 100-sample period.
    """

    def __init__(self, startV, endV, v_steps, duty):
        self.startV = startV
        self.endV = endV
        self.v_steps = v_steps
        self.duty = duty
        self.on = duty
        self.off = 100 - duty
        self.arry = None

    def voltages(self):
        v = np.linspace(self.startV, self.endV, self.v_steps)
        return np.float32(v * 32767)

    def wf_generator(self):
        self.arry = np.empty(0)
        vols = self.voltages()
        for x in vols:
            self.arry = np.append(self.arry, np.full(self.off, 0))
            self.arry = np.append(self.arry, np.full(self.on, x))
        # trailing zero padding after last pulse
        self.arry = np.append(self.arry, np.full(self.off, 0))
        pd.DataFrame(self.arry).to_csv(self.get_path(), header=False, index=False)

    def get_path(self):
        waveform_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'waveforms')
        waveform_dir = os.path.normpath(waveform_dir)
        os.makedirs(waveform_dir, exist_ok=True)
        fname = 'AW_{}Vto{}V_duty{}%_vsteps{}.csv'.format(
            self.startV, self.endV, self.duty, self.v_steps
        )
        return os.path.join(waveform_dir, fname)

    def get_arry(self):
        return self.arry


if __name__ == '__main__':
    wf = wf_settings(0, 1, 100, 50)
    wf.wf_generator()
    plt.plot(wf.arry)
    plt.title('Waveform preview')
    plt.xlabel('Sample index')
    plt.ylabel('DAC value')
    plt.show()
