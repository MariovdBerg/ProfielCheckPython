"""
Profiel datamodel
Converted from Profiel.cs, ProfielPunt.cs and ProfielDeel.cs
Copyright © 2016, 2017 HKV Services (original C# code)
Copyright © 2025-2026 HKV lijn in water B.V. (Python code)
Licensed under the EUPL
SPDX-License-Identifier: EUPL-1.2
Author: Rolf Waterman
Co-authors: Mario van den Berg, Claude

Profiel Hydra/Ringtoets: punten, profieldelen en het profiel zelf.
Inlezen, wegschrijven en valideren staan in reader.py, writer.py en checks.py.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass

from .profiel_enums import DamType, Damwandmodule, ProfielDeelType, ProfielVersion


@dataclass
class ProfielPunt:
    """Profile point with X coordinate (m), Z height (m+NAP) and roughness."""

    x: float = 0.0
    z: float = 0.0
    r: float = 1.0

    def zelfde_locatie(self, other):
        """True als beide punten dezelfde X en Z hebben (de ruwheid telt niet mee)."""
        return self.x == other.x and self.z == other.z

    def __str__(self):
        return f"ProfielPunt: X={self.x}, Z={self.z}, R={self.r}"


@dataclass
class ProfielDeel:
    """Profile section representing a segment of the profile."""

    x1: float = 0.0  # Afstand van (m)
    z1: float = 0.0  # Hoogte van (m+NAP)
    x2: float = 0.0  # Afstand tot (m)
    z2: float = 0.0  # Hoogte tot (m+NAP)
    r: float = 0.0   # Ruwheid
    profiel_deel_type: ProfielDeelType = ProfielDeelType.VOORLAND

    @classmethod
    def tussen(cls, begin, eind, profiel_deel_type):
        """Maak het profieldeel van punt `begin` naar punt `eind`, met de ruwheid van `begin`."""
        return cls(begin.x, begin.z, eind.x, eind.z, begin.r, profiel_deel_type)

    @property
    def tan_a(self):
        """Tangens van alpha (dz/dx); 0 bij een verticaal deel."""
        delta_x = self.x2 - self.x1
        return (self.z2 - self.z1) / delta_x if delta_x != 0 else 0.0

    @property
    def helling(self):
        """Helling als 1 op n; 0 bij een horizontaal deel."""
        tan_a = self.tan_a
        return 0.0 if tan_a == 0 else 1.0 / tan_a

    def __str__(self):
        return (f"{self.profiel_deel_type.name}: ({self.x1},{self.z1})\t"
                f"({self.x2},{self.z2})\tr={self.r:.1f}\t1:{self.helling:.1f}")


def _als_enum(enum_cls, waarde):
    """
    Zet `waarde` om naar een lid van `enum_cls`.

    Een ongeldige waarde wordt ongewijzigd teruggegeven, zodat check() er
    ERROR800/ERROR801 voor kan geven in plaats van een exception.
    """
    if isinstance(waarde, enum_cls):
        return waarde
    try:
        return enum_cls(waarde)
    except ValueError:
        return waarde


class Profiel:
    """
    Profile for Hydra/Ringtoets.

    Een profiel bestaat uit voorlandpunten en dijkpunten (teen tot kruin). Het laatste
    voorlandpunt en het eerste dijkpunt zijn normaal hetzelfde punt (de teen).
    """

    def __init__(
        self,
        *,
        id: str = "Onbekend000",
        versie: float = 4.0,
        damtype: DamType | int = DamType.GEEN,
        damhoogte: float = math.nan,
        richting: float = math.nan,
        kruinhoogte: float = math.nan,
        damwand: Damwandmodule | int = Damwandmodule.GEEN,
        voorland_punten: Iterable[ProfielPunt] = (),
        dijk_punten: Iterable[ProfielPunt] = (),
        memo: str = "",
        invoerfouten: Iterable[str] = (),
    ):
        """
        Initialize a new instance of Profiel.

        Args:
            id: Profielnaam
            versie: Versie van het bestandsformaat waaruit het profiel komt
            damtype: DamType (of de bijbehorende int)
            damhoogte: Damhoogte (m+NAP)
            richting: Dijknormaal (graden t.o.v. noord)
            kruinhoogte: Kruinhoogte (m+NAP)
            damwand: Damwandmodule (of de bijbehorende int)
            voorland_punten: Punten van het voorland; het laatste punt is de teen
            dijk_punten: Punten van de dijk, van teen tot kruin
            memo: Vrije tekst
            invoerfouten: Problemen die bij het inlezen zijn gevonden; check() geeft dan INVOER
        """
        self.id = id or "Onbekend000"
        self.versie = versie
        self.damtype = _als_enum(DamType, damtype)
        self.damhoogte = damhoogte
        self.richting = richting
        self.kruinhoogte = kruinhoogte
        self.damwand = _als_enum(Damwandmodule, damwand)
        self.voorland_punten = list(voorland_punten)
        self.dijk_punten = list(dijk_punten)
        self.memo = memo
        self.invoerfouten = list(invoerfouten)

    @classmethod
    def from_punten(cls, profielpunten: Iterable[ProfielPunt], voorland: int = 0, **kwargs):
        """
        Maak een profiel uit één lijst punten waarvan de eerste `voorland` punten het voorland zijn.

        Het laatste voorlandpunt is ook het eerste dijkpunt (de teen).

        Args:
            profielpunten: Alle profielpunten, van voorland tot kruin
            voorland: Aantal voorlandpunten (0 = geen voorland)
            **kwargs: Overige argumenten van Profiel()
        """
        punten = list(profielpunten)
        invoerfouten = []
        if voorland > len(punten):
            invoerfouten.append(
                f"VOORLAND ({voorland}) is groter dan het aantal profielpunten ({len(punten)})")
        if voorland > 0:
            return cls(voorland_punten=punten[:voorland], dijk_punten=punten[voorland - 1:],
                       invoerfouten=invoerfouten, **kwargs)
        return cls(dijk_punten=punten, invoerfouten=invoerfouten, **kwargs)

    @classmethod
    def from_string(cls, profiel_data: str):
        """Lees een profiel (versie 3 of 4) uit een tekst."""
        from .reader import read_string
        return read_string(profiel_data)

    @classmethod
    def from_file(cls, file_path, encoding: str | None = None):
        """
        Lees een profiel (versie 3 of 4) uit een bestand.

        Zonder encoding wordt UTF-8 gebruikt, met een waarschuwing en cp1252 als dat niet lukt.
        """
        from .reader import read_file
        return read_file(file_path, encoding=encoding)

    @property
    def voorland(self):
        """Aantal voorlandpunten."""
        return len(self.voorland_punten)

    @property
    def dijk(self):
        """Aantal dijkpunten."""
        return len(self.dijk_punten)

    @property
    def talud_punten(self):
        """
        De punten van de teen tot de kruin.

        Als de dijk niet begint op het laatste voorlandpunt, begint het talud bij dat voorlandpunt.
        """
        if self.voorland_punten and not (
                self.dijk_punten and self.dijk_punten[0].zelfde_locatie(self.voorland_punten[-1])):
            return [self.voorland_punten[-1], *self.dijk_punten]
        return list(self.dijk_punten)

    @property
    def profiel_punten(self):
        """Alle punten van voorland tot kruin, zonder het gedeelde teenpunt dubbel te tellen."""
        if not self.voorland_punten:
            return list(self.dijk_punten)
        return self.voorland_punten[:-1] + self.talud_punten

    @property
    def profiel_delen(self):
        """De profieldelen: eerst het voorland, dan het talud."""
        voorland = self.voorland_punten
        talud = self.talud_punten
        return ([ProfielDeel.tussen(a, b, ProfielDeelType.VOORLAND) for a, b in zip(voorland, voorland[1:])]
                + [ProfielDeel.tussen(a, b, ProfielDeelType.TALUD) for a, b in zip(talud, talud[1:])])

    def check(self):
        """
        Validate the profile.

        Returns:
            ProfielError enum indicating validation result
        """
        from .checks import check
        return check(self)

    def to_string(self, version=ProfielVersion.VERSION_4):
        """Geef het profiel als tekst in het formaat van versie 3 of 4."""
        from .writer import write_string
        return write_string(self, version)

    def save(self, file_path, version=ProfielVersion.VERSION_4, encoding: str = "utf-8"):
        """
        Save profile to file.

        Args:
            file_path: Path to save file
            version: ProfielVersion (or 3 / 4)
            encoding: Encoding of the file

        Raises:
            ValueError: for an unknown version
        """
        content = self.to_string(version)
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)

    def __str__(self):
        return (f"Profiel(id={self.id}, version={self.versie}, "
                f"points={len(self.profiel_punten)}, sections={len(self.profiel_delen)})")
