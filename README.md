# ProfielCheckPython

A Python port of the HKV C# library for reading, writing and validating Hydra/Ringtoets
profiles (`.prfl`): cross-sections of a dike with an optional foreland (voorland) and dam.

**Authors:** Rolf Waterman (original C# code), Mario van den Berg, Claude  
**Copyright:** © 2025-2026 HKV lijn in water B.V.; original C# code © 2016, 2017 HKV Services  
**License:** [EUPL-1.2](LICENSE)  
**Version:** 2.0.0 (see [CHANGELOG.md](CHANGELOG.md); not compatible with the C# library or 1.0.1.0)

## Overview

- Read and write profiles in the version 3 and version 4 file format, and convert between them
- Validate a profile against the Hydra/Ringtoets rules, with a specific error code per rule
- Read numbers with a point or a comma as decimal separator, independent of the locale
- No external dependencies

## Installation

The module is not (yet) an installable package: there is no `pyproject.toml`, so `pip install`
does not work. The code lives in the folder `src` and is imported as `src`.

### From source

```bash
git clone https://github.com/MariovdBerg/ProfielCheckPython.git
cd ProfielCheckPython
python example_usage.py
```

Scripts in the project folder can then use `from src import ...` directly.

### Direct use from another project

Add the project folder (the folder that *contains* `src`) to the Python path:

```python
import sys
sys.path.append(r"C:\path\to\ProfielCheckPython")

from src import Profiel, ProfielPunt, ProfielError
```

## Quick Start

### Creating a profile

```python
from src import Damwandmodule, DamType, Profiel, ProfielPunt, ProfielVersion

# Profile points: x (m), z (m+NAP), roughness
punten = [
    ProfielPunt(0.0, 2.0, 0.8),   # foreland
    ProfielPunt(20.0, 2.5, 0.8),  # dike toe: last foreland point and first dike point
    ProfielPunt(28.0, 3.5, 0.8),  # dike
    ProfielPunt(32.0, 5.5, 0.7),  # dike, up to the crest
]

profiel = Profiel.from_punten(
    punten,
    voorland=2,                   # the first 2 points are the foreland (0 = no foreland)
    id="PROFILE001",
    damtype=DamType.GEEN,
    damhoogte=1.0,
    richting=45.0,
    kruinhoogte=8.0,
    damwand=Damwandmodule.GEEN,
    memo="Example profile",
)

# Validate the profile
result = profiel.check()
print(f"Validation: {result.name} - {result.description}")   # Validation: OK - Profiel is ok.

# Save to file (default: version 4)
profiel.save("profile_v3.prfl", ProfielVersion.VERSION_3)
profiel.save("profile_v4.prfl")
```

`Profiel(...)` itself takes the foreland and dike points as two separate lists
(`voorland_punten=...`, `dijk_punten=...`), as in a version 4 file. All arguments are
keyword arguments; a misspelled argument raises a `TypeError`. Values that are not given
are `NaN` (numbers) or `GEEN` (dam type and dam wall).

### Reading a profile

```python
from src import Profiel

profiel = Profiel.from_file("profile_v4.prfl")   # version 3 or 4, detected from VERSIE
text = profiel.to_string(3)                      # the same profile in the version 3 format
profiel = Profiel.from_string(text)              # read from a string

print(profiel.voorland, profiel.dijk)            # number of foreland / dike points
print(profiel.profiel_punten)                    # all points, the toe counted once
print(profiel.profiel_delen)                     # the sections between the points
print(profiel.invoerfouten)                      # lines that could not be read
```

Lines that cannot be read are logged with `logging` and stored in `invoerfouten`;
`check()` then returns `ProfielError.INVOER`. Unknown keywords are only logged.

Files are read as UTF-8 (with or without BOM). If a file is not valid UTF-8, a warning
is logged with the file name and line number, and the file is read as cp1252 instead.
Pass `encoding=...` to `from_file()` to use one specific encoding without fallback.

## File Format

| | Version 3 | Version 4 |
|---|---|---|
| Separator | tab | space |
| Profile name | not stored | `ID` |
| Points | one list after `VOORLAND n`, preceded by a line `0.000 0.000 0.000` | `VOORLAND n` followed by n foreland points, `DIJK m` followed by m dike points |
| Dike toe | shared: the n-th point is both the last foreland point and the first dike point | written twice: last foreland point and first dike point |
| No foreland | `VOORLAND 1` (only the toe) | `VOORLAND 0` |

Each point is `x z roughness`. Everything after the line `MEMO` is the memo.

## Validation Rules

`check()` returns the first error it finds, as a `ProfielError` with a `code` and a
Dutch `description`:

| Code | Rule |
|---|---|
| OK | The profile is valid |
| INVOER | Unreadable lines, inconsistent point counts, or a foreland of 1 point |
| 101-104 | Foreland: x increasing, no point below the first point, at least 10 m between points, slopes at most 1:10 |
| 105 | No points at all (and no dam wall) |
| 111-115 | Dike: x and z increasing, at least 0.1 m between points, slopes between 1:100 and 1:1 |
| 116 | A dike section between a berm (up to 1:15) and a slope (from 1:8) |
| 117-120 | No two berms in a row, first and last section must be a slope, at most 2 berms |
| 121 | Roughness of the dike sections between 0.5 and 1.0 |
| 122 | Crest height high enough above the start of the last section |
| 130 | Dam wall (crest height) above the end of the foreland |
| 800, 801 | Invalid dam type or dam wall module |

The limits are constants in `src/checks.py`. A missing (`NaN`) crest height or roughness
is reported as an error.

## Module Structure

- **model.py**: `ProfielPunt`, `ProfielDeel` and `Profiel` (data only)
- **reader.py**: `read_file()`, `read_string()` for version 3 and 4
- **writer.py**: `write_string()` for version 3 and 4
- **checks.py**: `check()` and the validation constants
- **convert_string.py**: `parse_float()`, `parse_int()`, `format_float()`
- **profiel_enums.py**: `ProfielError`, `DamType`, `ProfielDeelType`, `Damwandmodule`, `ProfielVersion`

## Examples

Run the example script from the project folder:

```bash
python example_usage.py
```

This demonstrates:
1. Creating a profile from a list of points
2. Reading a version 3 profile from a string
3. Reading a version 4 profile from a string
4. Saving as version 4 and reading the file back
5. Validation errors for an invalid profile and an unreadable line

`test/test_example_usage.py` runs these examples, so they stay valid.

## Testing

The tests use pytest, pytest-cov and ruff (`requirements-dev.txt`). On Windows:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest --cov=src --cov-branch
.venv/Scripts/python -m ruff check src test example_usage.py
```

On Linux or macOS, use `.venv/bin/python` instead of `.venv/Scripts/python`.

## Requirements

- Python 3.9 or higher
- No external dependencies (only for testing, see above)

## License

Copyright © 2016, 2017 HKV Services (original C# code)  
Copyright © 2025-2026 HKV lijn in water B.V. (Python code)

Licensed under the EUPL

This work is licensed under the [European Union Public Licence v1.2](LICENSE) (EUPL-1.2),
an open-source licence with copyleft: you may use, change and distribute the code, also
commercially, provided that you keep the copyright notices, include the licence, mark your
changes, and distribute changed versions under the EUPL (or a compatible licence listed in
its appendix). The official text in all EU languages is available at
<https://interoperable-europe.ec.europa.eu/collection/eupl/eupl-text-eupl-12>.

## Credits

- **Original author:** Rolf Waterman (HKV), C# library `daas.fn` (2016, 2017)
- **Python version:** Mario van den Berg and Claude (Anthropic)
