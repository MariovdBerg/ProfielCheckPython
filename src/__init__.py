"""
ProfielCheckPython
Converted from C# - HKV Services
Copyright © 2016, 2017 HKV Services (original C# code)
Copyright © 2025-2026 HKV lijn in water B.V. (Python code)
Licensed under the EUPL
SPDX-License-Identifier: EUPL-1.2

Profiel Hydra/Ringtoets functionality in Python
"""

from .checks import check
from .convert_string import format_float, parse_float, parse_int
from .model import Profiel, ProfielDeel, ProfielPunt
from .profiel_enums import DamType, Damwandmodule, ProfielDeelType, ProfielError, ProfielVersion
from .reader import read_file, read_string
from .writer import write_string

__version__ = "2.0.0"
__all__ = [
    'ProfielError',
    'DamType',
    'ProfielDeelType',
    'Damwandmodule',
    'ProfielVersion',
    'ProfielPunt',
    'ProfielDeel',
    'Profiel',
    'check',
    'read_file',
    'read_string',
    'write_string',
    'parse_float',
    'parse_int',
    'format_float',
]
