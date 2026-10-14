# daas.fn - Python Module

A Python port of the C# daas.fn library for Profiel Hydra/Ringtoets profile validation and manipulation.

**Original Author:** Rolf Waterman  
**Copyright:** © HKV Services 2016, 2017  
**Version:** 1.0.1.0

## Overview

This Python module provides functionality for working with hydraulic engineering profiles (cross-sections of dikes, dams, and foreshores). It includes:

- Profile data structures (points and sections)
- Profile validation with detailed error checking
- Support for multiple profile versions (v3 and v4)
- String conversion utilities for handling different number formats
- File I/O for reading and writing profile data

## Installation

### From source:

```bash
# Clone or download the repository
cd /path/to/daas_fn

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Direct use:

```python
# Add the module directory to your Python path
import sys
sys.path.append('/path/to/daas_fn')

from daas_fn import Profiel, ProfielPunt, ProfielError
```

## Quick Start

### Creating a Profile from Scratch

```python
from src import Profiel, ProfielPunt, ProfielVersion

# Create profile points (x, z, roughness)
punten = [
    ProfielPunt(0.0, 2.0, 0.8),
    ProfielPunt(20.0, 2.5, 0.8),
    ProfielPunt(28.0, 3.5, 0.8),
    ProfielPunt(32.0, 5.5, 0.7),
]

# The first `voorland` points are the foreland; the last of them is also the dike toe
profiel = Profiel.from_punten(
    punten,
    voorland=2,
    id="PROFILE001",
    damtype=0,
    damhoogte=1.0,
    richting=45.0,
    kruinhoogte=8.0,
    damwand=0,
    memo="Example profile",
)

# Validate the profile
result = profiel.check()
print(f"Validation: {result.name} - {result.description}")

# Save to file (default: version 4)
profiel.save("profile_v3.prfl", ProfielVersion.VERSION_3)
profiel.save("profile_v4.prfl")
```

`Profiel(...)` itself takes the foreland and dike points separately
(`voorland_punten=...`, `dijk_punten=...`), as in a version 4 file.

### Reading a Profile

```python
from src import Profiel

profiel = Profiel.from_file("profile_v4.prfl")      # version 3 or 4
profiel = Profiel.from_string(profile_data)          # same, from a string
text = profiel.to_string(3)                          # convert to version 3

print(profiel.voorland, profiel.dijk)                # number of foreland / dike points
print(profiel.profiel_punten)                        # all points, toe counted once
print(profiel.invoerfouten)                          # lines that could not be read
```

Lines that cannot be read are logged (`logging`) and stored in `invoerfouten`;
`check()` then returns `ProfielError.INVOER`. Numbers may use a point or a comma as
decimal separator, independent of the locale.

Files are read as UTF-8 (with or without BOM). If a file is not valid UTF-8, a warning
is logged with the file name and line number, and the file is read as cp1252 instead.
Pass `encoding=...` to `from_file()` to use one specific encoding without fallback.

## Module Structure

- **model.py**: `ProfielPunt`, `ProfielDeel` and `Profiel` (data only)
- **reader.py**: `read_file()`, `read_string()` for version 3 and 4
- **writer.py**: `write_string()` for version 3 and 4
- **checks.py**: `check()` and the validation constants
- **convert_string.py**: `parse_float()`, `parse_int()`, `format_float()`
- **profiel_enums.py**: `ProfielError`, `DamType`, `ProfielDeelType`, `Damwandmodule`, `ProfielVersion`

## Validation Rules

The `check()` method validates profiles against constraints including:

- Input: unreadable lines, inconsistent point counts (INVOER)
- Foreland: point ordering, heights, distances, slopes (ERROR101-104)
- Dike sections: ordering, slopes, berms, roughness 0.5-1.0, crest height (ERROR111-122)
- Dam/wall: type validation, height constraints (ERROR130, ERROR800-801)

## Testing

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest --cov=src --cov-branch
.venv/Scripts/python -m ruff check src test
```

## Examples

Run the comprehensive example script:

```bash
python example_usage.py
```

This demonstrates:
1. Creating profiles from scratch
2. Parsing profile data
3. String conversion utilities
4. Validation error handling
5. All error types enumeration

## Requirements

- Python 3.9 or higher
- No external dependencies

## License

Original C# code: Copyright © HKV Services 2016, 2017

## Credits

- **Original Author:** Rolf Waterman (HKV Consultants)
- **Python Conversion:** 2025
