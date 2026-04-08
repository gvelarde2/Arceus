# Contributing to Arceus

## Development setup

```bash
git clone https://github.com/gvelarde2/Arceus.git
cd Arceus
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
```

A NI-VISA or compatible VISA backend must also be installed for instrument communication. For hardware-free development and testing, `pyvisa-sim` can simulate instrument responses.

## Running tests

```bash
pytest tests/
```

The test suite covers utility modules (`DataDirectory`, `wf_settings`) and does not require any connected instruments. Instrument driver tests would need a running VISA simulation or real hardware.

## Adding an instrument driver

1. Create `src/Arceus/instruments/<manufacturer>_<model>.py`.
2. Define a class named after the instrument (e.g. `class HP34970A`).
3. Accept `resource` as a constructor parameter with the default VISA address as a module-level constant — this makes it easy to override in tests or when the address changes.
4. Keep all instrument logic in the driver. Measurement sequencing belongs in `measurements/`.

## Adding a measurement

1. Create `src/Arceus/measurements/<name>.py`.
2. Import only from `arceus.instruments.*` and `arceus.utils.*` — no direct pyvisa calls.
3. Provide a `__main__` block with sensible defaults so the script can be run standalone.

## Coding style

- PEP 8 naming: `snake_case` for functions and variables, `UpperCamelCase` for classes.
- Keep VISA resource address strings as module-level constants so they are easy to find and change.
- Do not hardcode absolute paths inside functions; use `DataDirectory` or pass paths as parameters.

## Submitting changes

1. Fork the repo and create a branch: `git checkout -b feature/my-change`
2. Make your changes and add tests where applicable.
3. Run `pytest tests/` and confirm it passes.
4. Open a pull request against `main` with a description of what changed and why.
