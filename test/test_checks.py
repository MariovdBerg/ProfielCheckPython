import math

import pytest

from src import Damwandmodule, Profiel, ProfielError, ProfielPunt, checks

from .conftest import punten


def maak(coordinaten, voorland=0, kruinhoogte=5.0, **kwargs):
    return Profiel.from_punten(punten(*coordinaten), voorland=voorland, kruinhoogte=kruinhoogte, **kwargs)


# (beschrijving, coordinaten, voorland, kruinhoogte, verwachte fout)
CASES = [
    ("geldig zonder voorland", [(0, 0), (8, 1)], 0, 2.0, ProfielError.OK),
    ("geldig met voorland", [(0, 0), (20, 1), (28, 2), (32, 4)], 2, 5.0, ProfielError.OK),
    ("talud - berm - talud", [(0, 0), (4, 2), (24, 3), (28, 5)], 0, 5.0, ProfielError.OK),
    ("voorland > aantal punten", [(0, 0), (100, 1)], 5, 5.0, ProfielError.INVOER),
    ("voorland van 1 punt", [(0, 0), (100, 1)], 1, 5.0, ProfielError.INVOER),
    ("101 voorland x daalt", [(10, 0), (5, 1)], 2, 5.0, ProfielError.ERROR101),
    ("101 voorland x gelijk", [(10, 0), (10, 1)], 2, 5.0, ProfielError.ERROR101),
    ("102 voorland onder eerste punt", [(0, 2), (15, 1)], 2, 5.0, ProfielError.ERROR102),
    ("103 voorlandpunten < 10 m", [(0, 0), (5, 0.1)], 2, 5.0, ProfielError.ERROR103),
    ("104 voorland steiler dan 1:10", [(0, 0), (10, 5)], 2, 10.0, ProfielError.ERROR104),
    ("111 dijk x daalt", [(10, 0), (5, 1)], 0, 5.0, ProfielError.ERROR111),
    ("112 dijk z daalt", [(0, 2), (10, 1)], 0, 5.0, ProfielError.ERROR112),
    ("112 dijk z gelijk", [(0, 2), (10, 2)], 0, 5.0, ProfielError.ERROR112),
    ("113 dijkpunten < 0.1 m", [(0, 0), (0.05, 0.01)], 0, 5.0, ProfielError.ERROR113),
    ("114 steiler dan 1:1", [(0, 0), (1, 2)], 0, 5.0, ProfielError.ERROR114),
    ("115 flauwer dan 1:100", [(0, 0), (200, 1)], 0, 5.0, ProfielError.ERROR115),
    ("116 tussen berm en talud", [(0, 0), (10, 1)], 0, 5.0, ProfielError.ERROR116),
    ("117 twee bermen achter elkaar", [(0, 0), (20, 1), (40, 2)], 0, 5.0, ProfielError.ERROR117),
    ("118 eerste deel geen talud", [(0, 0), (20, 1)], 0, 5.0, ProfielError.ERROR118),
    ("119 laatste deel geen talud", [(0, 0), (8, 1), (28, 2)], 0, 5.0, ProfielError.ERROR119),
    ("120 drie bermen", [(0, 0), (8, 1), (28, 2), (36, 3), (56, 4), (64, 5), (84, 6), (92, 7)],
     0, 10.0, ProfielError.ERROR120),
    ("122 kruinhoogte te laag", [(0, 0), (8, 1)], 0, 0.1, ProfielError.ERROR122),
]


@pytest.mark.parametrize("coordinaten, voorland, kruinhoogte, verwacht",
                         [case[1:] for case in CASES], ids=[case[0] for case in CASES])
def test_check(coordinaten, voorland, kruinhoogte, verwacht):
    assert maak(coordinaten, voorland, kruinhoogte).check() == verwacht


def test_check_functie_gelijk_aan_methode():
    profiel = maak([(0, 0), (8, 1)], kruinhoogte=2.0)
    assert checks.check(profiel) == profiel.check()


def test_error105_geen_punten():
    assert Profiel().check() == ProfielError.ERROR105


def test_geen_punten_met_damwand_is_ok():
    assert Profiel(damwand=Damwandmodule.DAMWAND).check() == ProfielError.OK


def test_invoerfouten_geven_invoer():
    profiel = Profiel(dijk_punten=punten((0, 0), (8, 1)), kruinhoogte=2.0, invoerfouten=["regel 3 onleesbaar"])
    assert profiel.check() == ProfielError.INVOER


# --- B4: ontbrekende kruinhoogte ---------------------------------------------

def test_b4_ontbrekende_kruinhoogte():
    assert maak([(0, 0), (8, 1)], kruinhoogte=math.nan).check() == ProfielError.ERROR122


# --- B5: ongeldige damtype / damwand ----------------------------------------

@pytest.mark.parametrize("damtype", [-1, 4, 7, "x"])
def test_b5_ongeldige_damtype(damtype):
    assert maak([(0, 0), (8, 1)], kruinhoogte=2.0, damtype=damtype).check() == ProfielError.ERROR800


@pytest.mark.parametrize("damwand", [-1, 3, 9])
def test_b5_ongeldige_damwand(damwand):
    assert maak([(0, 0), (8, 1)], kruinhoogte=2.0, damwand=damwand).check() == ProfielError.ERROR801


# --- ERROR130: damwand ------------------------------------------------------

VOORLAND_EN_DIJK = [(0, 0), (20, 1), (28, 2), (32, 4)]


@pytest.mark.parametrize("damwand", [Damwandmodule.DAMWAND, Damwandmodule.DAMWAND_PLUS_NEUS])
def test_damwand_boven_voorland_ok(damwand):
    assert maak(VOORLAND_EN_DIJK, voorland=2, kruinhoogte=5.0, damwand=damwand).check() == ProfielError.OK


def test_error130_damwand_niet_boven_voorland():
    profiel = Profiel(voorland_punten=punten((0, 0), (20, 1)), kruinhoogte=1.0, damwand=Damwandmodule.DAMWAND)
    assert profiel.check() == ProfielError.ERROR130


def test_error130_ontbrekende_kruinhoogte():
    profiel = Profiel(voorland_punten=punten((0, 0), (20, 1)), damwand=Damwandmodule.DAMWAND)
    assert profiel.check() == ProfielError.ERROR130


# --- Grenswaarden -----------------------------------------------------------

def talud_met_middendeel(tan_a):
    """Talud 1:2, een middendeel met helling tan_a over 20 m, talud 1:2."""
    return [ProfielPunt(0, 0), ProfielPunt(4, 2), ProfielPunt(24, 2 + 20 * tan_a), ProfielPunt(28, 4 + 20 * tan_a)]


@pytest.mark.parametrize("tan_a, verwacht", [
    (checks.TANAMIN, ProfielError.OK),            # precies 1:100 is toegestaan
    (checks.TANAMIN * 0.99, ProfielError.ERROR115),
    (checks.TANAFLW, ProfielError.OK),            # precies 1:15 is een berm
    (checks.TANAFLW * 1.001, ProfielError.ERROR116),  # net steiler dan 1:15 is geen berm meer
    (checks.TANASTL, ProfielError.OK),            # precies 1:8 is een talud
    (0.1, ProfielError.ERROR116),
    (checks.TANAMAX, ProfielError.OK),            # precies 1:1 is toegestaan
])
def test_grens_helling_middendeel(tan_a, verwacht):
    profiel = Profiel(dijk_punten=talud_met_middendeel(tan_a), kruinhoogte=50.0)
    assert profiel.check() == verwacht


def test_grens_helling_steiler_dan_tanamax():
    profiel = Profiel(dijk_punten=punten((0, 0), (1, 1.001)), kruinhoogte=20.0)
    assert profiel.check() == ProfielError.ERROR114


@pytest.mark.parametrize("delta_x, verwacht", [
    (checks.DELTAXMINVOORLAND, ProfielError.OK),
    (checks.DELTAXMINVOORLAND - 0.01, ProfielError.ERROR103),
])
def test_grens_afstand_voorland(delta_x, verwacht):
    profiel = maak([(0, 0), (delta_x, 0.5), (delta_x + 8, 1.5)], voorland=2)
    assert profiel.check() == verwacht


@pytest.mark.parametrize("delta_z, verwacht", [
    (1.0, ProfielError.OK),        # helling precies 1:10
    (1.001, ProfielError.ERROR104),
])
def test_grens_helling_voorland(delta_z, verwacht):
    profiel = maak([(0, 0), (10, delta_z), (18, delta_z + 1)], voorland=2)
    assert profiel.check() == verwacht


@pytest.mark.parametrize("delta_x, verwacht", [
    (checks.DELTAXMINDIJK, ProfielError.OK),
    (0.09, ProfielError.ERROR113),
])
def test_grens_afstand_dijk(delta_x, verwacht):
    profiel = maak([(0, 0), (delta_x, delta_x)])
    assert profiel.check() == verwacht


@pytest.mark.parametrize("kruinhoogte, verwacht", [
    (1.25, ProfielError.OK),       # precies 2 * tan_a boven het begin van het laatste deel
    (1.2499, ProfielError.ERROR122),
])
def test_grens_kruinhoogte(kruinhoogte, verwacht):
    assert maak([(0, 1), (8, 2)], kruinhoogte=kruinhoogte).check() == verwacht


def test_precies_twee_bermen_is_ok():
    profiel = maak([(0, 0), (8, 1), (28, 2), (36, 3), (56, 4), (64, 5)], kruinhoogte=10.0)
    assert profiel.check() == ProfielError.OK


def test_voorland_punt_gelijk_aan_eerste_is_ok():
    profiel = maak([(0, 1), (20, 1), (28, 2)], voorland=2)
    assert profiel.check() == ProfielError.OK


# --- Volgorde van de controles -----------------------------------------------

def test_damtype_wordt_voor_invoer_gecontroleerd():
    profiel = maak([(0, 0), (100, 1)], voorland=5, damtype=9)
    assert profiel.check() == ProfielError.ERROR800


def test_voorland_wordt_voor_dijk_gecontroleerd():
    profiel = maak([(0, 0), (5, 0.1), (4, 3)], voorland=2)
    assert profiel.check() == ProfielError.ERROR103


# --- ERROR121: ruwheid ------------------------------------------------------

def dijk_met_ruwheid(*ruwheden):
    """Dijk van drie delen (talud - berm - talud) plus kruinpunt, met de gegeven ruwheden per punt."""
    coordinaten = [(0, 0), (4, 2), (24, 3), (28, 5)]
    return Profiel(dijk_punten=[ProfielPunt(x, z, r) for (x, z), r in zip(coordinaten, ruwheden)],
                   kruinhoogte=10.0)


@pytest.mark.parametrize("ruwheid, verwacht", [
    (checks.RUWHEIDLAAG, ProfielError.OK),          # grenzen zijn toegestaan
    (checks.RUWHEIDHOOG, ProfielError.OK),
    (0.75, ProfielError.OK),
    (checks.RUWHEIDLAAG - 0.01, ProfielError.ERROR121),
    (checks.RUWHEIDHOOG + 0.01, ProfielError.ERROR121),
    (0.0, ProfielError.ERROR121),
    (-0.8, ProfielError.ERROR121),
    (math.nan, ProfielError.ERROR121),
])
def test_ruwheid_grenzen(ruwheid, verwacht):
    assert dijk_met_ruwheid(ruwheid, ruwheid, ruwheid, 1.0).check() == verwacht


@pytest.mark.parametrize("positie", [0, 1, 2])
def test_ruwheid_van_elk_dijkdeel_wordt_gecontroleerd(positie):
    ruwheden = [0.8, 0.8, 0.8, 0.8]
    ruwheden[positie] = 0.3
    assert dijk_met_ruwheid(*ruwheden).check() == ProfielError.ERROR121


def test_ruwheid_van_kruinpunt_telt_niet_mee():
    """Het laatste punt begint geen profieldeel, dus zijn ruwheid wordt niet gebruikt."""
    assert dijk_met_ruwheid(0.8, 0.8, 0.8, 0.0).check() == ProfielError.OK


def test_ruwheid_van_voorland_telt_niet_mee():
    voorland = [ProfielPunt(0, 0, 0.0), ProfielPunt(20, 1, 0.8)]
    dijk = [ProfielPunt(20, 1, 0.8), ProfielPunt(28, 2, 0.8), ProfielPunt(32, 4, 0.8)]
    assert Profiel(voorland_punten=voorland, dijk_punten=dijk, kruinhoogte=5.0).check() == ProfielError.OK


def test_ruwheid_van_teen_komt_uit_dijkpunten():
    """In versie 4 staat de teen twee keer; de ruwheid van het dijkpunt geldt voor het eerste dijkdeel."""
    voorland = [ProfielPunt(0, 0, 0.8), ProfielPunt(20, 1, 0.3)]
    dijk = [ProfielPunt(20, 1, 0.8), ProfielPunt(28, 2, 0.8), ProfielPunt(32, 4, 0.8)]
    assert Profiel(voorland_punten=voorland, dijk_punten=dijk, kruinhoogte=5.0).check() == ProfielError.OK
    dijk[0] = ProfielPunt(20, 1, 0.3)
    assert Profiel(voorland_punten=voorland, dijk_punten=dijk, kruinhoogte=5.0).check() == ProfielError.ERROR121


def test_geometrie_wordt_voor_ruwheid_gecontroleerd():
    profiel = Profiel(dijk_punten=[ProfielPunt(0, 0, 0.3), ProfielPunt(10, 1, 0.3)], kruinhoogte=5.0)
    assert profiel.check() == ProfielError.ERROR116


def test_error121_enum():
    assert ProfielError.ERROR121.code == 121
    assert "ruwheid" in ProfielError.ERROR121.description.lower()
