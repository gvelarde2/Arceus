"""
Arceus — entry point.

Intended to become a GUI that dispatches any measurement from a single
interface. For now, runs a temperature calibration sweep directly.
"""
import asyncio

from arceus.measurements.temp_cal import main as run_temp_cal

if __name__ == "__main__":
    asyncio.run(run_temp_cal(rep='multi', setpoint=30, Istart=50e-6, Istop=500e-6, Iden=10))
