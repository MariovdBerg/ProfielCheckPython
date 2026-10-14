"""
Profiel Enums
Converted from ProfielEnums.cs
Copyright © HKV Services 2016, 2017
Author: Rolf Waterman
"""

from enum import Enum


class ProfielError(Enum):
    """Profielerrorcode."""

    OK = (0, "Profiel is ok.")
    ONBEKEND = (1, "Er is een onbekende fout ontstaan.")
    INVOER = (2, "Invoer niet correct.")
    ERROR101 = (101, "De profielpunten in de kolom 'afstand' lopen niet op gezien over het voorland richting het talud.")
    ERROR102 = (102, "Eén van de profielpunten van het voorland ligt lager dan het eerste profielpunt van het voorland.")
    ERROR103 = (103, "De onderlinge afstand van de profielpunten van het voorland is kleiner dan 10 meter.")
    ERROR104 = (104, "Hellingen steiler dan 1 op 10 zijn niet toegestaan op het voorland.")
    ERROR105 = (105, "Het aantal profielpunten moet groter zijn dan 0.")
    ERROR111 = (111, "De profielpunten in de kolom 'afstand' lopen niet op gezien vanaf de teen naar de kruin van de dijk.")
    ERROR112 = (112, "De hoogtes van de profielpunten moeten oplopen gezien vanaf de teen naar de kruin van de dijk.")
    ERROR113 = (113, "De afstand tussen twee profielpunten is minder dan 0.1 meter.")
    ERROR114 = (114, "Er komt een te steil taluddeel voor (steiler dan 1 op 1).")
    ERROR115 = (115, "Er komt een te flauw taluddeel voor (flauwer dan 1 op 100).")
    ERROR116 = (116, "Er komt een taluddeel voor dat qua steilheid tussen een berm en een talud inligt (steiler dan 1 op 15 en flauwer dan 1 op 8).")
    ERROR117 = (117, "Er komen twee opeenvolgende bermen voor (taluddelen met een helling flauwer dan 1 op 15).")
    ERROR118 = (118, "Het eerste profieldeel is geen talud (flauwer dan 1 op 8).")
    ERROR119 = (119, "Het laatste profieldeel is geen talud (flauwer dan 1 op 8).")
    ERROR120 = (120, "Er komen meer dan twee bermen voor (taluddelen met een helling flauwer dan 1 op 15).")
    ERROR121 = (121, "De ruwheid van een dijkdeel ligt niet tussen 0.5 en 1.0.")
    ERROR122 = (122, "De kruinhoogte ligt onvoldoende hoog op het laatste profieldeel.")
    ERROR130 = (130, "De hoogte van de damwand ligt niet boven het eindpunt van het voorland.")
    ERROR800 = (800, "Waarde voor damtype is niet correct. Mogelijke waarden zijn: 0: Geen dam, 1: Caisson, 2: Steile wand, 3: Havendam.")
    ERROR801 = (801, "Waarde voor damwandmodule is niet correct. Mogelijke waarden zijn: 0: Geen, 1: Damwand, 2: Damwand plus neus.")

    def __init__(self, code, description):
        self.code = code
        self.description = description


class DamType(Enum):
    """Dam type."""

    GEEN = 0  # Geen dam
    CAISSON = 1  # Caisson
    STEILE_WAND = 2  # Steile wand
    HAVENDAM = 3  # Havendam


class ProfielDeelType(Enum):
    """ProfielDeelType."""

    VOORLAND = 0  # The voorland
    TALUD = 1  # The talud


class Damwandmodule(Enum):
    """Damwandmodule."""

    GEEN = 0  # Geen damwand
    DAMWAND = 1  # Damwand
    DAMWAND_PLUS_NEUS = 2  # Damwand plus neus


class ProfielVersion(Enum):
    """Profiel Version."""

    VERSION_3 = 3
    VERSION_4 = 4
