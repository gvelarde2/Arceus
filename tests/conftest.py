"""
Shared pytest fixtures and configuration.

Instrument drivers open VISA connections at import time in some modules.
Tests that exercise only utility code (DataDirectory, waveform) run fine
without any hardware or VISA backend. If you add tests that import
instrument drivers directly, mock the pyvisa.ResourceManager at the
session level here, e.g.:

    @pytest.fixture(autouse=True)
    def mock_visa(monkeypatch):
        import pyvisa
        monkeypatch.setattr(pyvisa, "ResourceManager", MockResourceManager)
"""
import pytest


@pytest.fixture
def sample_waveform_params():
    """Standard waveform parameters used across multiple tests."""
    return dict(startV=0, endV=1, v_steps=100, duty=50)
