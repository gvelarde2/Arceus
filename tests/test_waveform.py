"""Tests for the wf_settings waveform builder."""
import os

import numpy as np
import pytest

from arceus.utils.waveform import wf_settings


def test_waveform_length():
    wf = wf_settings(startV=0, endV=1, v_steps=10, duty=50)
    wf.wf_generator()
    # Each step = off(50) + on(50) samples, plus one trailing off block
    expected = 10 * 100 + 50
    assert len(wf.arry) == expected


def test_waveform_starts_and_ends_at_zero():
    wf = wf_settings(0, 1, 5, 50)
    wf.wf_generator()
    assert wf.arry[0] == 0
    assert wf.arry[-1] == 0


def test_voltage_scaling():
    wf = wf_settings(0, 1, 2, 50)
    vols = wf.voltages()
    # 0V → 0 DAC, 1V → 32767 DAC (float32)
    assert vols[0] == pytest.approx(0.0, abs=1)
    assert vols[-1] == pytest.approx(32767.0, abs=1)


def test_csv_created(tmp_path, monkeypatch):
    # Redirect output to tmp_path
    monkeypatch.chdir(tmp_path)
    os.makedirs(tmp_path / 'data' / 'waveforms', exist_ok=True)

    wf = wf_settings(0, 1, 10, 50)
    # Patch get_path to write inside tmp_path
    wf.get_path = lambda: str(tmp_path / 'data' / 'waveforms' / 'test_wf.csv')
    wf.wf_generator()

    assert os.path.isfile(str(tmp_path / 'data' / 'waveforms' / 'test_wf.csv'))


def test_duty_cycle_off_samples():
    wf = wf_settings(0, 1, 1, 30)  # duty=30 → on=30, off=70
    wf.wf_generator()
    # First 70 samples should be zero (off period)
    assert all(wf.arry[:70] == 0)
    # Next 30 should be non-zero (on period at last voltage step which is also first)
    assert all(wf.arry[70:100] != 0)
