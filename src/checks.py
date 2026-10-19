"""
Profielcontrole
Converted from Profiel.cs (Check)
Copyright © 2016, 2017 HKV Services (original C# code)
Copyright © 2025-2026 HKV lijn in water B.V. (Python code)
Licensed under the EUPL
SPDX-License-Identifier: EUPL-1.2
Author: Rolf Waterman
Co-authors: Mario van den Berg, Claude

Validatie van een profiel volgens de regels van Hydra/Ringtoets.
"""

from .profiel_enums import DamType, Damwandmodule, ProfielError

# Constants
TANAMINVOORLAND = 0.1  # Maximale helling voor voorland
TANAMIN = 0.01  # Minimal helling voor profieldeel
TANAMAX = 1.0  # Maximale helling voor profieldeel
TANAFLW = 1.0 / 15.0  # Minimal helling voor flauw profieldeel
TANASTL = 0.125  # Maximale helling voor steil profieldeel
TANABERM = 1.0 / 15.0  # Profieldelen met een helling tot en met 1 op 15 tellen als berm
DELTAXMINVOORLAND = 10.0  # Minimale afstand tussen de voorlandpunten
DELTAXMINDIJK = 0.1  # Minimale afstand tussen de dijkpunten
NBERMEN = 2  # Maximale aantal bermen
RUWHEIDLAAG = 0.5  # Minimale ruwheid van een dijkdeel
RUWHEIDHOOG = 1.0  # Maximale ruwheid van een dijkdeel


def check(profiel):
    """
    Validate the profile.

    Bij meerdere fouten wordt de eerste gevonden fout teruggegeven.

    Returns:
        ProfielError enum indicating validation result
    """
    if not isinstance(profiel.damtype, DamType):
        return ProfielError.ERROR800
    if not isinstance(profiel.damwand, Damwandmodule):
        return ProfielError.ERROR801
    if profiel.invoerfouten:
        return ProfielError.INVOER

    fout = _check_voorland(profiel.voorland_punten)
    if fout:
        return fout

    if not profiel.voorland_punten and not profiel.dijk_punten:
        return ProfielError.ERROR105 if profiel.damwand == Damwandmodule.GEEN else ProfielError.OK

    # Zonder dijkdeel (één punt, of alleen voorland) is het geen dijkprofiel; bij een damwand mag dat wel
    if len(profiel.talud_punten) < 2 and profiel.damwand == Damwandmodule.GEEN:
        return ProfielError.INVOER

    fout = _check_dijk(profiel.talud_punten, profiel.kruinhoogte) or _check_ruwheid(profiel.talud_punten)
    if fout:
        return fout

    # De damwand (op kruinhoogte) moet boven het eind van het voorland uitkomen
    if profiel.damwand != Damwandmodule.GEEN and profiel.voorland_punten:
        if not profiel.kruinhoogte > profiel.voorland_punten[-1].z:
            return ProfielError.ERROR130

    return ProfielError.OK


def _segmenten(punten):
    """Geef (dx, dz) voor elk segment tussen opeenvolgende punten."""
    return [(b.x - a.x, b.z - a.z) for a, b in zip(punten, punten[1:])]


def _check_voorland(punten):
    """Controleer het voorland; None als het voorland in orde (of afwezig) is."""
    if not punten:
        return None
    if len(punten) < 2:
        return ProfielError.INVOER

    segmenten = _segmenten(punten)
    if any(delta_x <= 0 for delta_x, _ in segmenten):
        return ProfielError.ERROR101
    eerste_z = punten[0].z
    if any(punt.z < eerste_z for punt in punten[1:]):
        return ProfielError.ERROR102
    if any(delta_x < DELTAXMINVOORLAND for delta_x, _ in segmenten):
        return ProfielError.ERROR103
    if any(abs(delta_z / delta_x) > TANAMINVOORLAND for delta_x, delta_z in segmenten):
        return ProfielError.ERROR104
    return None


def _check_dijk(punten, kruinhoogte):
    """Controleer de dijk (teen tot kruin); None als de dijk in orde is."""
    tan_as = []
    for delta_x, delta_z in _segmenten(punten):
        if delta_x <= 0:
            return ProfielError.ERROR111
        if delta_z <= 0:
            return ProfielError.ERROR112
        if delta_x < DELTAXMINDIJK:
            return ProfielError.ERROR113

        tan_a = delta_z / delta_x
        if tan_a > TANAMAX:
            return ProfielError.ERROR114
        if tan_a < TANAMIN:
            return ProfielError.ERROR115
        if TANAFLW < tan_a < TANASTL:
            return ProfielError.ERROR116
        tan_as.append(tan_a)

    if not tan_as:
        return None

    if any(a <= TANAFLW and b <= TANAFLW for a, b in zip(tan_as, tan_as[1:])):
        return ProfielError.ERROR117
    if tan_as[0] < TANASTL:
        return ProfielError.ERROR118
    if tan_as[-1] < TANASTL:
        return ProfielError.ERROR119
    # Geschreven als 'not >=' zodat een ontbrekende (NaN) kruinhoogte ook een fout geeft
    if not kruinhoogte >= punten[-2].z + 2 * tan_as[-1]:
        return ProfielError.ERROR122
    if sum(1 for tan_a in tan_as if tan_a <= TANABERM) > NBERMEN:
        return ProfielError.ERROR120
    return None


def _check_ruwheid(punten):
    """
    Controleer de ruwheid van de dijkdelen; None als die in orde is.

    De ruwheid van een deel is die van zijn beginpunt, dus de ruwheid van het laatste punt (kruin)
    telt niet mee. Het voorland wordt niet gecontroleerd: daar wordt geen ruwheid gebruikt.
    """
    # Geschreven als 'not ... <= ...' zodat een ontbrekende (NaN) ruwheid ook een fout geeft
    if any(not RUWHEIDLAAG <= punt.r <= RUWHEIDHOOG for punt in punten[:-1]):
        return ProfielError.ERROR121
    return None
