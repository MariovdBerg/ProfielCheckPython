import logging
import math

import pytest

from prflcheck import DamType, Damwandmodule, Profiel, ProfielError, ProfielPunt, read_file, read_string

from .conftest import fixture_path

# Verwachte waarden per testbestand: (bestand, versie, id, damtype, damhoogte, richting, kruinhoogte,
#                                     damwand, aantal voorlandpunten, aantal dijkpunten, memo)
DAM_VARIANTEN = [
    ("caisson", "V4_CAISSON", DamType.CAISSON, 5.0, 45.0, Damwandmodule.GEEN),
    ("steile_wand", "V4_STEILE_WAND", DamType.STEILE_WAND, 3.0, 270.0, Damwandmodule.GEEN),
    ("havendam", "V4_HAVENDAM", DamType.HAVENDAM, 4.5, 180.0, Damwandmodule.GEEN),
    ("damwand", "V4_DAMWAND", DamType.GEEN, 0.0, 90.0, Damwandmodule.DAMWAND),
    ("damwand_plus_neus", "V4_DAMWAND_PLUS_NEUS", DamType.GEEN, 0.0, 90.0, Damwandmodule.DAMWAND_PLUS_NEUS),
]

FIXTURES = [
    ("read_test_profile_v3.prfl", 3.0, "Onbekend000", DamType.GEEN, 1.5, 90.0, 8.5,
     Damwandmodule.GEEN, 3, 4, "Read v3 test\n"),
    ("read_test_profile_v4.prfl", 4.0, "READ_V4", DamType.GEEN, 0.0, 25.0, 9.4,
     Damwandmodule.GEEN, 2, 4, "Read v4 test\n"),
]
for _naam, _id, _damtype, _damhoogte, _richting, _damwand in DAM_VARIANTEN:
    # In versie 3 betekent VOORLAND 1 "geen voorland" (B7), net als VOORLAND 0 in versie 4
    FIXTURES.append((f"read_test_profile_v3_{_naam}.prfl", 3.0, "Onbekend000", _damtype, _damhoogte,
                     _richting, 8.0, _damwand, 0, 2, None))
    FIXTURES.append((f"read_test_profile_v4_{_naam}.prfl", 4.0, _id, _damtype, _damhoogte,
                     _richting, 8.0, _damwand, 0, 2, None))


@pytest.mark.parametrize(
    "bestand, versie, id_, damtype, damhoogte, richting, kruinhoogte, damwand, n_voorland, n_dijk, memo",
    FIXTURES, ids=[f[0] for f in FIXTURES])
def test_lees_testbestand(bestand, versie, id_, damtype, damhoogte, richting, kruinhoogte,
                          damwand, n_voorland, n_dijk, memo):
    profiel = Profiel.from_file(fixture_path(bestand))

    assert profiel.versie == versie
    assert profiel.id == id_
    assert profiel.damtype == damtype
    assert profiel.damhoogte == damhoogte
    assert profiel.richting == richting
    assert profiel.kruinhoogte == kruinhoogte
    assert profiel.damwand == damwand
    assert profiel.voorland == n_voorland
    assert profiel.dijk == n_dijk
    if memo is not None:
        assert profiel.memo == memo
    assert profiel.invoerfouten == []
    # Alle testbestanden zijn geldige profielen (B1 en B7: dit ging eerder mis)
    assert profiel.check() == ProfielError.OK


def test_lees_v3_punten():
    profiel = read_file(fixture_path("read_test_profile_v3.prfl"))
    assert profiel.voorland_punten == [ProfielPunt(0, 2, 0.8), ProfielPunt(15, 2.5, 0.8), ProfielPunt(30, 3, 0.8)]
    assert profiel.dijk_punten[0] == ProfielPunt(30, 3, 0.8)
    assert profiel.dijk_punten[-1] == ProfielPunt(45, 8.5, 0.7)
    assert len(profiel.profiel_punten) == 6


def test_lees_v4_punten_zonder_dubbel_teenpunt():
    """B1: het teenpunt staat in het bestand twee keer, maar is één profielpunt."""
    profiel = read_file(fixture_path("read_test_profile_v4.prfl"))
    assert profiel.voorland_punten == [ProfielPunt(0, 3, 1), ProfielPunt(100, 4, 1)]
    assert profiel.dijk_punten[0] == ProfielPunt(100, 4, 1)
    xs = [p.x for p in profiel.profiel_punten]
    assert xs == [0.0, 100.0, 110.5, 125.0, 130.0]


def test_from_string_gelijk_aan_read_string():
    tekst = fixture_path("read_test_profile_v4.prfl").read_text(encoding="utf-8")
    a, b = Profiel.from_string(tekst), read_string(tekst)
    assert (a.voorland_punten, a.dijk_punten, a.memo) == (b.voorland_punten, b.dijk_punten, b.memo)


V3_TEKST = """VERSIE	3.0
DAM		0
DAMHOOGTE	1.5
RICHTING	90.0
KRUINHOOGTE	8.5
VOORLAND	1
DAMWAND		0
0.000	0.000	0.000
0.000	2.000	0.8
8.000	3.000	0.8
MEMO
Test profile
"""


def test_v3_eerste_nulregel_wordt_overgeslagen():
    profiel = read_string(V3_TEKST)
    assert profiel.profiel_punten == [ProfielPunt(0, 2, 0.8), ProfielPunt(8, 3, 0.8)]
    assert profiel.memo == "Test profile\n"


def test_crlf_regeleinden():
    profiel = read_string(V3_TEKST.replace("\n", "\r\n"))
    assert profiel.dijk == 2
    assert profiel.memo == "Test profile\n"


def test_letterlijke_backslash_n():
    profiel = read_string(V3_TEKST.replace("\n", "\\n"))
    assert profiel.dijk == 2
    assert profiel.kruinhoogte == 8.5


def test_komma_als_decimaalteken():
    profiel = read_string(V3_TEKST.replace("8.5", "8,5").replace("0.8", "0,8"))
    assert profiel.kruinhoogte == 8.5
    assert profiel.dijk_punten[0].r == 0.8


def test_memo_meerdere_regels_en_lege_regels():
    profiel = read_string(V3_TEKST.replace("Test profile\n", "regel 1\n\nregel 2   \n"))
    assert profiel.memo == "regel 1\nregel 2\n"


def test_memo_met_sleutelwoorden_wordt_niet_geparsed():
    profiel = read_string(V3_TEKST.replace("Test profile\n", "DAM 3\n1 2 3\n"))
    assert profiel.damtype == DamType.GEEN
    assert profiel.dijk == 2
    assert profiel.memo == "DAM 3\n1 2 3\n"


def test_id_met_spaties():
    profiel = read_string("VERSIE 4.0\nID dijkvak 12 a\nVOORLAND 0\nDIJK 0\n")
    assert profiel.id == "dijkvak 12 a"


def test_lege_tekst():
    profiel = read_string("")
    assert profiel.profiel_punten == []
    assert profiel.invoerfouten == []


def test_versie_ontbreekt_v4_herkend_aan_dijk():
    profiel = read_string("VOORLAND 0\nDIJK 2\n0 2 0.8\n8 3 0.8\nKRUINHOOGTE 8\n")
    assert profiel.versie == 4.0
    assert profiel.dijk == 2
    assert profiel.check() == ProfielError.OK


def test_versie_ontbreekt_v3():
    profiel = read_string("VOORLAND 1\n0 0 0\n0 2 0.8\n8 3 0.8\nKRUINHOOGTE 8\n")
    assert profiel.versie == 3.0
    assert profiel.check() == ProfielError.OK


def test_ontbrekende_waarden_zijn_nan():
    profiel = read_string("VERSIE 4.0\nVOORLAND 0\nDIJK 0\n")
    assert math.isnan(profiel.kruinhoogte)
    assert math.isnan(profiel.richting)
    assert math.isnan(profiel.damhoogte)


def test_nan_wordt_gelezen():
    profiel = read_string("VERSIE 4.0\nDAMHOOGTE NaN\nVOORLAND 0\nDIJK 0\n")
    assert math.isnan(profiel.damhoogte)
    assert profiel.invoerfouten == []


# --- Ongeldige invoer --------------------------------------------------------

@pytest.mark.parametrize("vervang, door", [
    ("KRUINHOOGTE	8.5", "KRUINHOOGTE	hoog"),
    ("KRUINHOOGTE	8.5", "KRUINHOOGTE"),
    ("VOORLAND	1", "VOORLAND	1.5"),
    ("8.000	3.000	0.8", "8.000	3.000"),
    ("8.000	3.000	0.8", "8.000	3.000	0.8	1.0"),
    ("8.000	3.000	0.8", "8.000	drie	0.8"),
], ids=["tekst als getal", "waarde ontbreekt", "voorland geen geheel getal",
        "punt zonder ruwheid", "punt met 4 waarden", "punt met tekst"])
def test_onleesbare_regel_geeft_invoer(vervang, door, caplog):
    with caplog.at_level(logging.WARNING):
        profiel = read_string(V3_TEKST.replace(vervang, door))
    assert len(profiel.invoerfouten) == 1
    assert profiel.check() == ProfielError.INVOER
    assert "kan niet worden gelezen" in caplog.text


def test_onbekend_sleutelwoord_wordt_gelogd_maar_is_geen_fout(caplog):
    with caplog.at_level(logging.WARNING):
        profiel = read_string(V3_TEKST.replace("MEMO", "ONBEKEND 12\nMEMO"))
    assert profiel.invoerfouten == []
    assert profiel.check() == ProfielError.OK
    assert "ONBEKEND 12" in caplog.text


@pytest.mark.parametrize("damtype", ["4", "-1"])
def test_ongeldige_dam_in_bestand_geeft_error800(damtype):
    profiel = read_string(V3_TEKST.replace("DAM		0", f"DAM		{damtype}"))
    assert profiel.check() == ProfielError.ERROR800


def test_ongeldige_damwand_in_bestand_geeft_error801():
    profiel = read_string(V3_TEKST.replace("DAMWAND		0", "DAMWAND		5"))
    assert profiel.check() == ProfielError.ERROR801


def test_v3_voorland_groter_dan_aantal_punten():
    profiel = read_string(V3_TEKST.replace("VOORLAND	1", "VOORLAND	5"))
    assert profiel.check() == ProfielError.INVOER


V4_TEKST = """VERSIE 4.0
ID X
VOORLAND 2
0.000 3.000 1.000
100.000 4.000 1.000
KRUINHOOGTE 9.4
DIJK 2
100.000 4.000 1.000
108.000 5.000 1.000
"""


def test_v4_geldig():
    assert read_string(V4_TEKST).check() == ProfielError.OK


@pytest.mark.parametrize("vervang, door", [
    ("VOORLAND 2", "VOORLAND 3"),
    ("DIJK 2", "DIJK 3"),
    ("ID X", "ID X\n1.0 2.0 1.0"),
], ids=["voorland telt niet", "dijk telt niet", "punt buiten sectie"])
def test_v4_inconsistente_secties_geven_invoer(vervang, door):
    profiel = read_string(V4_TEKST.replace(vervang, door))
    assert len(profiel.invoerfouten) == 1
    assert profiel.check() == ProfielError.INVOER


def test_v4_nulpunt_wordt_niet_overgeslagen():
    tekst = "VERSIE 4.0\nVOORLAND 0\nDIJK 2\n0 0 0\n8 1 0\n"
    assert read_string(tekst).dijk == 2
