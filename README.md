# Arceus

Automated electrical test bench characterization suite for diode device testing at Purdue. Controls lab instruments over VISA to run temperature calibration sweeps, diode I-V characterization, and real-time thermal monitoring.

---

## Instruments

| Driver | Instrument | Interface | Role |
|---|---|---|---|
| `agilent_34401a.py` | Agilent 34401A DMM | GPIB0::4 | DC voltage and 2-pt/4-pt resistance measurement |
| `agilent_4156.py` | Agilent 4156 Parameter Analyzer | GPIB0::2 | I-V sweeps via pymeasure |
| `keithley_2110.py` | Keithley 2110 DMM | USB | Thermocouple temperature readout |
| `keithley_6220.py` | Keithley 6220 Current Source | GPIB0::12 | Precision DC current sourcing |
| `keysight_e36312a.py` | Keysight E36312A Power Supply | USB | Voltage/current control for device heating |
| `keysight_awg.py` | Keysight 33600A AWG | USB | Arbitrary waveform output from CSV |
| `rigol_mso5074.py` | Rigol MSO5074 Oscilloscope | USB | Waveform capture and export |

---

## Repository structure

```
Arceus/
├── src/Arceus/
│   ├── instruments/          # One driver class per instrument
│   ├── measurements/         # Test sequences that orchestrate instruments
│   │   ├── temp_cal.py       # Temperature calibration current sweep
│   │   ├── diode_sweep.py    # Diode heating + I-V characterization
│   │   └── live_temp_read.py # Real-time voltage-to-temperature monitor
│   ├── utils/
│   │   ├── data_directory.py # Date-stamped save path builder
│   │   └── waveform.py       # Ramped pulse-train waveform generator
│   └── main.py               # Entry point (future GUI)
├── config/
│   └── config_diode.json     # Agilent 4156 SMU channel configuration
├── data/
│   └── waveforms/            # Pre-generated AWG waveform CSV files
├── notebooks/                # Exploratory Jupyter notebooks
└── tests/                    # pytest test suite
```

---

## Measurements

### Temperature calibration (`temp_cal.py`)

Steps a Keithley 6220 current source from `Istart` to `Istop` in `Iden` steps. At each step, a K2110 thermocouple DMM and an A34401A voltage DMM log concurrently (via `asyncio.gather`) for a configurable hold time. Data is saved as time-stamped CSVs.

```python
from arceus.measurements.temp_cal import main
import asyncio

asyncio.run(main(rep='multi', setpoint=30, Istart=50e-6, Istop=500e-6, Iden=10))
# rep='single' runs one step at 100 µA
```

### Diode heating sweep (`diode_sweep.py`)

Ramps a Keysight E36312A power supply through a voltage range to heat the device under test. At each voltage step the Agilent 4156 parameter analyzer collects a configurable number of I-V sweeps, then the supply turns off and a cool-down period elapses before the next step.

```python
from arceus.measurements.diode_sweep import diode_sweep
from arceus.instruments.agilent_4156 import connect
import numpy as np

smu = connect()
diode_sweep(
    voltage_steps=np.round(np.linspace(0, 3, 121), 3),
    current_limit=0.55,
    iterations=11,
    smu=smu,
    cool_t=1800,
    save_path='C:\\Lab_Data\\Data\\D00',
)
```

### Live temperature monitor (`live_temp_read.py`)

Continuously reads voltage from the A34401A and converts it to °C using the calibration curve determined by `temp_cal`. Runs until `Ctrl-C`, then saves the full trace to CSV.

```python
from arceus.measurements.live_temp_read import LiveTempReader

reader = LiveTempReader()
reader.run(deviceID=1, comment='D01_stability')
```

The conversion coefficients are defined at the top of the file and should be updated after each calibration run:

```python
CAL_INTERCEPT = 0.72    # V
CAL_SLOPE     = -0.0020243  # V/°C
```

---

## Utilities

### DataDirectory

Builds and creates date-stamped save paths of the form `<root>\YYYYMMDD\D###_<comment>\`.

```python
from arceus.utils.data_directory import DataDirectory

dd = DataDirectory(dID=1, comment='tcal_run1')
print(dd.path())
# C:\Lab_Data\Data\20260408\D001_tcal_run1\

# Organise flat CSV files into per-setpoint subdirectories
dd2 = DataDirectory(directory='C:\\Lab_Data\\Data\\20260408\\D001', key='Iset')
dd2.file_organizer()
```

The default root is `C:\Lab_Data\Data`. Pass `root=` to override:

```python
DataDirectory(dID=2, root='D:\\MyData')
```

### Waveform generator

Produces a ramped pulse-train compatible with the Keysight 33600A DAC format and saves it as a CSV in `data/waveforms/`.

```python
from arceus.utils.waveform import wf_settings

wf = wf_settings(startV=0, endV=1, v_steps=100, duty=50)
wf.wf_generator()          # writes CSV and populates wf.arry
print(wf.get_path())       # data/waveforms/AW_0Vto1V_duty50%_vsteps100.csv
```

---

## Agilent 4156 configuration

`config/config_diode.json` defines the SMU channel mapping for diode I-V sweeps:

```json
{
  "SMU1": { "channel_function": "VAR1", "channel_mode": "V", ... },
  "SMU3": { "channel_function": "CONS", "channel_mode": "COMM" },
  "VAR1": { "start": 0, "stop": 1, "step": 0.01, "compliance": 0.1 }
}
```

Pass a different path to `agilent_4156.connect(config_path=...)` to use an alternate configuration.

> **Note:** `agilent_4156.py` includes a placeholder `run_sweep()` function. The `smu.measure()` and `smu.get_data()` calls inside it should be verified against the pymeasure `Agilent4156` API and your specific measurement configuration before use.

---

## Installation

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode along with `pytest` for running tests.

**Dependencies:** `pyvisa`, `numpy`, `pandas`, `matplotlib`, `pymeasure`

A NI-VISA or compatible VISA backend (e.g. `pyvisa-py`) must be installed and configured separately for instrument communication.

---

## Running tests

```bash
pytest tests/
```

Tests cover `DataDirectory` path construction and file organisation, and `wf_settings` waveform generation. They do not require any connected instruments.

---

## Data layout

All measurement data is saved under `C:\Lab_Data\Data\` by default:

```
C:\Lab_Data\Data\
└── YYYYMMDD\
    └── D###_<comment>\
        ├── TimevsTemp_TsetC_30_Iset_1.00e-04.csv
        ├── TimevsVolt_TsetC_30_Iset_1.00e-04.csv
        └── ...
```

After a run, `DataDirectory.file_organizer()` can sort flat CSV files into per-setpoint subdirectories keyed on a filename token (e.g. `Iset`).
