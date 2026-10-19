import math

import pytest

from prflcheck import (
    DamType,
    Damwandmodule,
    Profiel,
    ProfielError,
    ProfielPunt,
    ProfielVersion,
    read_file,
    write_string,
)

from .conftest import fixture_path, punten

VERSIES = [ProfielVersion.VERSION_3, ProfielVersion.VERSION_4]


def basis_profiel(**kwargs):
    waarden = dict(id="WRITE", damtype=DamType.GEEN, damhoogte=1.5, richting=90.0, kruinhoogte=8.5,
                   memo="Write test")
    waarden.update(kwargs)
    alle = [ProfielPunt(0.0, 2.0, 0.8), ProfielPunt(15.0, 2.5, 0.8), ProfielPunt(30.0, 3.0, 0.8),
            ProfielPunt(35.0, 5.0, 0.7), ProfielPunt(40.0, 7.5, 0.7), ProfielPunt(45.0, 8.5, 0.7)]
    return Profiel.from_punten(alle, voorland=3, **waarden)


def zonder_voorland(**kwargs):
    waarden = dict(damhoogte=0.0, richting=90.0, kruinhoogte=8.0, memo="Write test")
    waarden.update(kwargs)
    return Profiel.from_punten(punten((0.0, 2.0), (8.0, 3.0)), voorland=0, **waarden)


PROFIELEN = {
    "met voorland": basis_profiel,
    "caisson": lambda: zonder_voorland(damtype=DamType.CAISSON, damhoogte=5.0),
    "steile wand": lambda: zonder_voorland(damtype=DamType.STEILE_WAND, damhoogte=3.0),
    "havendam": lambda: zonder_voorland(damtype=DamType.HAVENDAM, damhoogte=4.5),
    "damwand": lambda: zonder_voorland(damwand=Damwandmodule.DAMWAND),
    "damwand plus neus": lambda: zonder_voorland(damwand=Damwandmodule.DAMWAND_PLUS_NEUS),
    "dijk sluit niet aan op voorland": lambda: Profiel(
        voorland_punten=punten((0, 1), (20, 2)), dijk_punten=punten((22, 2.5), (30, 3.5)), kruinhoogte=5.0),
    "ontbrekende waarden (NaN)": lambda: zonder_voorland(damhoogte=math.nan, richting=math.nan,
                                                         kruinhoogte=math.nan),
}


def assert_zelfde_profiel(gelezen, origineel, version):
    # dijk_punten zelf kan verschillen: een gat tussen voorland en dijk wordt als dijkdeel geschreven
    for veld in ("damtype", "damwand", "voorland_punten", "talud_punten", "profiel_punten", "profiel_delen"):
        assert getattr(gelezen, veld) == getattr(origineel, veld), veld
    for veld in ("damhoogte", "richting", "kruinhoogte"):
        a, b = getattr(gelezen, veld), getattr(origineel, veld)
        assert a == b or (math.isnan(a) and math.isnan(b)), veld
    assert gelezen.memo.strip() == origineel.memo.strip()
    assert gelezen.versie == ProfielVersion(version).value
    if ProfielVersion(version) == ProfielVersion.VERSION_4:
        assert gelezen.id == origineel.id  # versie 3 kent geen ID
    assert gelezen.invoerfouten == []
    assert gelezen.check() == origineel.check()


@pytest.mark.parametrize("version", VERSIES, ids=["v3", "v4"])
@pytest.mark.parametrize("naam", PROFIELEN)
def test_schrijven_en_teruglezen(naam, version, tmp_path):
    origineel = PROFIELEN[naam]()
    pad = tmp_path / "profiel.prfl"
    origineel.save(pad, version)
    assert_zelfde_profiel(read_file(pad), origineel, version)


@pytest.mark.parametrize("version", VERSIES, ids=["v3", "v4"])
@pytest.mark.parametrize("naam", PROFIELEN)
def test_schrijven_is_idempotent(naam, version):
    """Lezen en opnieuw schrijven geeft exact dezelfde tekst."""
    tekst = write_string(PROFIELEN[naam](), version)
    assert Profiel.from_string(tekst).to_string(version) == tekst


@pytest.mark.parametrize("version", VERSIES, ids=["v3", "v4"])
@pytest.mark.parametrize("bestand", ["read_test_profile_v3.prfl", "read_test_profile_v4.prfl"])
def test_testbestand_omzetten(bestand, version):
    """Een v3-bestand kan als v4 worden geschreven en andersom, zonder dat er iets verandert."""
    origineel = read_file(fixture_path(bestand))
    assert_zelfde_profiel(Profiel.from_string(origineel.to_string(version)), origineel, version)


def test_v4_formaat():
    assert basis_profiel().to_string(4) == "\n".join([
        "VERSIE 4.0", "ID WRITE", "", "RICHTING 90.0", "", "DAM 0", "DAMHOOGTE 1.5", "",
        "VOORLAND 3", "0.000 2.000 0.800", "15.000 2.500 0.800", "30.000 3.000 0.800", "",
        "DAMWAND 0", "KRUINHOOGTE 8.5", "DIJK 4",
        "30.000 3.000 0.800", "35.000 5.000 0.700", "40.000 7.500 0.700", "45.000 8.500 0.700",
        "", "MEMO", "Write test",
    ])


def test_v3_formaat():
    assert basis_profiel().to_string(3) == "\n".join([
        "VERSIE\t3.0", "DAM\t\t0", "DAMHOOGTE\t1.5", "RICHTING\t90.0", "KRUINHOOGTE\t8.5",
        "VOORLAND\t3", "DAMWAND\t\t0", "0.000\t0.000\t0.000",
        "0.000\t2.000\t0.800", "15.000\t2.500\t0.800", "30.000\t3.000\t0.800",
        "35.000\t5.000\t0.700", "40.000\t7.500\t0.700", "45.000\t8.500\t0.700",
        "MEMO", "Write test",
    ])


def test_v3_zonder_voorland_schrijft_voorland_1():
    assert "VOORLAND\t1" in zonder_voorland().to_string(3)


def test_b2_nan_wordt_als_nan_geschreven():
    tekst = zonder_voorland(damhoogte=math.nan).to_string(4)
    assert "DAMHOOGTE NaN" in tekst
    assert ".a." not in tekst


def test_ongeldige_damtype_wordt_geschreven_en_teruggelezen():
    profiel = zonder_voorland(damtype=7)
    assert Profiel.from_string(profiel.to_string(4)).check() == ProfielError.ERROR800


def test_standaard_versie_is_4(tmp_path):
    pad = tmp_path / "p.prfl"
    zonder_voorland().save(pad)
    assert read_file(pad).versie == 4.0


@pytest.mark.parametrize("version, eerste_regel", [
    (ProfielVersion.VERSION_3, "VERSIE\t3.0"), (3, "VERSIE\t3.0"),
    (ProfielVersion.VERSION_4, "VERSIE 4.0"), (4, "VERSIE 4.0"),
])
def test_versie_als_enum_of_int(version, eerste_regel):
    assert zonder_voorland().to_string(version).splitlines()[0] == eerste_regel


@pytest.mark.parametrize("version", [2, 5, "4"])
def test_onbekende_versie_geeft_fout(version, tmp_path):
    with pytest.raises(ValueError):
        zonder_voorland().save(tmp_path / "p.prfl", version)


def test_save_print_niets(tmp_path, capsys):
    zonder_voorland().save(tmp_path / "p.prfl")
    assert capsys.readouterr().out == ""
