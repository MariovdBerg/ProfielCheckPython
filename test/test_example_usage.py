"""Houdt example_usage.py werkend: de voorbeelden moeten de verwachte uitkomst geven."""

import example_usage
from src import ProfielError


def test_voorbeelden_1_tot_4_zijn_geldig(capsys):
    for voorbeeld in (example_usage.voorbeeld_1_profiel_aanmaken,
                      example_usage.voorbeeld_2_versie_3_lezen,
                      example_usage.voorbeeld_3_versie_4_lezen,
                      example_usage.voorbeeld_4_opslaan_en_omzetten):
        profiel = voorbeeld()
        assert profiel.check() == ProfielError.OK, voorbeeld.__name__
        assert profiel.invoerfouten == []


def test_voorbeeld_2_bevat_geen_nulpunt():
    profiel = example_usage.voorbeeld_2_versie_3_lezen()
    assert profiel.profiel_punten[0].x == -50.0
    assert profiel.memo == "Dit is een test profiel gemaakt met een string.\n"


def test_voorbeeld_4_behoudt_punten():
    origineel = example_usage.Profiel.from_string(example_usage.PROFIEL_V3)
    assert example_usage.voorbeeld_4_opslaan_en_omzetten().profiel_punten == origineel.profiel_punten


def test_voorbeeld_5_geeft_fouten(capsys):
    te_flauw, onleesbaar = example_usage.voorbeeld_5_fouten()
    assert te_flauw.check() == ProfielError.ERROR116
    assert onleesbaar.check() == ProfielError.INVOER


def test_main_draait(capsys):
    example_usage.main()
    assert "Alle voorbeelden voltooid!" in capsys.readouterr().out
