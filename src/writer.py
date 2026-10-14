"""
Profiel writer
Converted from Profiel.cs (Save)
Copyright © HKV Services 2016, 2017
Author: Rolf Waterman

Wegschrijven van profielen in het formaat van versie 3 en versie 4.
"""

from enum import Enum

from .convert_string import format_float
from .profiel_enums import ProfielVersion


def write_string(profiel, version=ProfielVersion.VERSION_4):
    """
    Geef het profiel als tekst.

    Args:
        profiel: Het profiel
        version: ProfielVersion (or 3 / 4)

    Raises:
        ValueError: for an unknown version
    """
    if ProfielVersion(version) == ProfielVersion.VERSION_3:
        lines = _lines_version_3(profiel)
    else:
        lines = _lines_version_4(profiel)
    return "\n".join(lines)


def _value(waarde):
    """Waarde van een enum; een ongeldige (niet-enum) waarde wordt ongewijzigd geschreven."""
    return waarde.value if isinstance(waarde, Enum) else waarde


def _point_lines(punten, separator):
    return [f"{p.x:.3f}{separator}{p.z:.3f}{separator}{p.r:.3f}" for p in punten]


def _lines_version_3(profiel):
    separator = "\t"
    if profiel.voorland_punten:
        punten = profiel.voorland_punten[:-1] + profiel.talud_punten
    else:
        punten = profiel.talud_punten

    return [
        f"VERSIE{separator}3.0",
        f"DAM{separator}{separator}{_value(profiel.damtype)}",
        f"DAMHOOGTE{separator}{format_float(profiel.damhoogte)}",
        f"RICHTING{separator}{format_float(profiel.richting)}",
        f"KRUINHOOGTE{separator}{format_float(profiel.kruinhoogte)}",
        # In versie 3 betekent VOORLAND 1: alleen de teen, dus geen voorland
        f"VOORLAND{separator}{max(profiel.voorland, 1)}",
        f"DAMWAND{separator}{separator}{_value(profiel.damwand)}",
        f"0.000{separator}0.000{separator}0.000",
        *_point_lines(punten, separator),
        "MEMO",
        profiel.memo.strip(),
    ]


def _lines_version_4(profiel):
    separator = " "
    talud_punten = profiel.talud_punten

    return [
        f"VERSIE{separator}4.0",
        f"ID{separator}{profiel.id}",
        "",
        f"RICHTING{separator}{format_float(profiel.richting)}",
        "",
        f"DAM{separator}{_value(profiel.damtype)}",
        f"DAMHOOGTE{separator}{format_float(profiel.damhoogte)}",
        "",
        f"VOORLAND{separator}{profiel.voorland}",
        *_point_lines(profiel.voorland_punten, separator),
        "",
        f"DAMWAND{separator}{_value(profiel.damwand)}",
        f"KRUINHOOGTE{separator}{format_float(profiel.kruinhoogte)}",
        f"DIJK{separator}{len(talud_punten)}",
        *_point_lines(talud_punten, separator),
        "",
        "MEMO",
        profiel.memo.strip(),
    ]
