import math

import pytest

from prflcheck import DamType, Damwandmodule, Profiel, ProfielDeel, ProfielDeelType, ProfielPunt

from .conftest import punten


class TestProfielPunt:
    def test_default_values(self):
        punt = ProfielPunt()
        assert (punt.x, punt.z, punt.r) == (0.0, 0.0, 1.0)

    def test_creation(self):
        punt = ProfielPunt(10.0, 5.0, 0.8)
        assert (punt.x, punt.z, punt.r) == (10.0, 5.0, 0.8)

    def test_gelijkheid(self):
        assert ProfielPunt(1.0, 2.0, 0.5) == ProfielPunt(1.0, 2.0, 0.5)
        assert ProfielPunt(1.0, 2.0, 0.5) != ProfielPunt(1.0, 2.0, 0.6)

    def test_zelfde_locatie_negeert_ruwheid(self):
        assert ProfielPunt(1.0, 2.0, 0.5).zelfde_locatie(ProfielPunt(1.0, 2.0, 1.0))
        assert not ProfielPunt(1.0, 2.0).zelfde_locatie(ProfielPunt(1.0, 2.1))

    def test_str(self):
        assert str(ProfielPunt(1.0, 2.0, 0.5)) == "ProfielPunt: X=1.0, Z=2.0, R=0.5"


class TestProfielDeel:
    def test_tan_a_en_helling(self):
        deel = ProfielDeel(x1=0.0, z1=0.0, x2=10.0, z2=5.0)
        assert deel.tan_a == pytest.approx(0.5)
        assert deel.helling == pytest.approx(2.0)

    def test_verticaal_deel(self):
        deel = ProfielDeel(x1=5.0, z1=0.0, x2=5.0, z2=5.0)
        assert deel.tan_a == 0.0
        assert deel.helling == 0.0

    def test_horizontaal_deel(self):
        deel = ProfielDeel(x1=0.0, z1=1.0, x2=10.0, z2=1.0)
        assert deel.tan_a == 0.0
        assert deel.helling == 0.0

    def test_tussen_neemt_ruwheid_van_beginpunt(self):
        deel = ProfielDeel.tussen(ProfielPunt(0, 1, 0.7), ProfielPunt(4, 3, 0.9), ProfielDeelType.TALUD)
        assert deel == ProfielDeel(0, 1, 4, 3, 0.7, ProfielDeelType.TALUD)

    def test_str(self):
        deel = ProfielDeel(0.0, 0.0, 8.0, 1.0, 0.8, ProfielDeelType.TALUD)
        assert str(deel) == "TALUD: (0.0,0.0)\t(8.0,1.0)\tr=0.8\t1:8.0"


class TestProfielCreation:
    def test_creation_empty(self):
        profiel = Profiel()
        assert profiel.id == "Onbekend000"
        assert profiel.versie == 4.0
        assert profiel.profiel_punten == []
        assert profiel.profiel_delen == []
        assert math.isnan(profiel.kruinhoogte)
        assert profiel.invoerfouten == []

    def test_lege_id_wordt_default(self):
        assert Profiel(id="").id == "Onbekend000"

    def test_onbekend_argument_geeft_fout(self):
        """Een tikfout in een argument wordt niet meer stil genegeerd."""
        with pytest.raises(TypeError):
            Profiel(damwandmodule=1)

    def test_creation_with_points(self):
        profiel = Profiel.from_punten(
            punten((0.0, 2.0), (10.0, 3.0)), voorland=0,
            id="TEST001", damtype=0, damhoogte=1.0, richting=45.0,
            kruinhoogte=8.0, damwand=0, memo="Test",
        )
        assert profiel.id == "TEST001"
        assert profiel.damtype == DamType.GEEN
        assert profiel.damhoogte == 1.0
        assert profiel.richting == 45.0
        assert profiel.kruinhoogte == 8.0
        assert profiel.voorland == 0
        assert profiel.dijk == 2
        assert profiel.damwand == Damwandmodule.GEEN
        assert profiel.memo == "Test"
        assert len(profiel.profiel_punten) == 2
        assert len(profiel.profiel_delen) == 1

    @pytest.mark.parametrize("waarde, verwacht", [
        (0, DamType.GEEN), (1, DamType.CAISSON), (2, DamType.STEILE_WAND),
        (3, DamType.HAVENDAM), (DamType.CAISSON, DamType.CAISSON),
    ])
    def test_damtype(self, waarde, verwacht):
        assert Profiel(damtype=waarde).damtype == verwacht

    @pytest.mark.parametrize("waarde, verwacht", [
        (0, Damwandmodule.GEEN), (1, Damwandmodule.DAMWAND),
        (2, Damwandmodule.DAMWAND_PLUS_NEUS), (Damwandmodule.DAMWAND, Damwandmodule.DAMWAND),
    ])
    def test_damwand(self, waarde, verwacht):
        assert Profiel(damwand=waarde).damwand == verwacht

    def test_ongeldige_enum_waarde_wordt_bewaard(self):
        """B5: een ongeldige damtype/damwand geeft geen exception meer."""
        profiel = Profiel(damtype=7, damwand=9)
        assert profiel.damtype == 7
        assert profiel.damwand == 9


class TestVoorlandEnDijk:
    def test_from_punten_deelt_teenpunt(self):
        alle = punten((0, 1), (20, 2), (30, 2.5), (35, 4))
        profiel = Profiel.from_punten(alle, voorland=3)
        assert profiel.voorland_punten == alle[:3]
        assert profiel.dijk_punten == alle[2:]
        assert profiel.voorland == 3
        assert profiel.dijk == 2
        assert profiel.profiel_punten == alle

    def test_from_punten_voorland_groter_dan_aantal_punten(self):
        profiel = Profiel.from_punten(punten((0, 0), (100, 1)), voorland=5)
        assert len(profiel.invoerfouten) == 1

    def test_dubbel_teenpunt_wordt_niet_dubbel_geteld(self):
        """B1: in versie 4 staat de teen zowel onder VOORLAND als onder DIJK."""
        voorland = punten((0, 3), (100, 4))
        dijk = [ProfielPunt(100, 4, 0.5), *punten((110, 6), (130, 9))]
        profiel = Profiel(voorland_punten=voorland, dijk_punten=dijk)
        assert profiel.profiel_punten == [voorland[0], *dijk]
        assert profiel.talud_punten == dijk

    def test_dijk_sluit_niet_aan_op_voorland(self):
        """Het talud begint dan op het laatste voorlandpunt."""
        voorland = punten((0, 3), (100, 4))
        dijk = punten((102, 4.5), (110, 6))
        profiel = Profiel(voorland_punten=voorland, dijk_punten=dijk)
        assert profiel.talud_punten == [voorland[-1], *dijk]
        assert profiel.profiel_punten == voorland + dijk

    def test_alleen_voorland(self):
        voorland = punten((0, 3), (100, 4))
        profiel = Profiel(voorland_punten=voorland)
        assert profiel.talud_punten == [voorland[-1]]
        assert profiel.profiel_punten == voorland

    def test_profiel_delen(self):
        alle = punten((0, 1), (20, 2), (30, 2.5), (35, 4))
        profiel = Profiel.from_punten(alle, voorland=2)
        types = [deel.profiel_deel_type for deel in profiel.profiel_delen]
        assert types == [ProfielDeelType.VOORLAND, ProfielDeelType.TALUD, ProfielDeelType.TALUD]
        assert profiel.profiel_delen[1] == ProfielDeel(20, 2, 30, 2.5, 0.8, ProfielDeelType.TALUD)

    def test_profiel_delen_volgen_wijzigingen(self):
        profiel = Profiel(dijk_punten=punten((0, 0), (8, 1)))
        profiel.dijk_punten.append(ProfielPunt(12, 3))
        assert len(profiel.profiel_delen) == 2

    def test_str(self):
        profiel = Profiel.from_punten(punten((0, 1), (20, 2), (30, 3)), voorland=2, id="X")
        assert str(profiel) == "Profiel(id=X, version=4.0, points=3, sections=2)"
