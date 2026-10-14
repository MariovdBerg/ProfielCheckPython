"""
Voorbeelden van het gebruik van de ProfielCheckPython-module.

Uitvoeren vanuit de hoofdmap van het project:
    python example_usage.py
"""

import tempfile
from pathlib import Path

from src import DamType, Damwandmodule, Profiel, ProfielPunt, ProfielVersion

PROFIEL_V3 = """VERSIE	3.0
DAM		0
DAMHOOGTE	0.0
RICHTING	90.0
KRUINHOOGTE	8.5
VOORLAND	3
DAMWAND		0
0.000	0.000	0.000
-50.000	1.000	0.8
0.000	2.000	0.8
15.000	2.500	0.8
17.000	3.000	0.8
24.000	5.000	0.7
40.000	5.300	0.7
50.000	8.000	0.7
MEMO
Dit is een test profiel gemaakt met een string.
"""

PROFIEL_V4 = """VERSIE 4.0
ID TEST0004

RICHTING 90.0

DAM 0
DAMHOOGTE 0.0

VOORLAND 2
-50.000 1.000 0.8
0.000 2.000 0.8

DAMWAND 0
KRUINHOOGTE 8.5
DIJK 5
0.000 2.000 0.8
6.000 3.000 0.8
26.000 3.800 0.8
32.000 5.500 0.7
37.000 8.000 0.7

MEMO
Dit is een test profiel gemaakt met een string.
"""


def kop(titel):
    print("=" * 60)
    print(titel)
    print("=" * 60)


def toon_profiel(profiel):
    """Print de eigenschappen, profieldelen en het resultaat van de controle."""
    print(f"Versie: {profiel.versie}")
    print(f"Profiel ID: {profiel.id}")
    print(f"Richting: {profiel.richting}")
    print(f"Dam type: {profiel.damtype.name}")
    print(f"Dam hoogte: {profiel.damhoogte}")
    print(f"Damwand: {profiel.damwand.name}")
    print(f"Kruinhoogte: {profiel.kruinhoogte}")
    print(f"Voorlandpunten: {profiel.voorland}")
    print(f"Dijkpunten: {profiel.dijk}")
    print(f"Profielpunten: {len(profiel.profiel_punten)}")
    print(f"Memo: {profiel.memo.strip()}")

    print("\nProfiel delen:")
    for i, deel in enumerate(profiel.profiel_delen, start=1):
        print(f"  {i}. {deel}")

    resultaat = profiel.check()
    print(f"\nValidatie: {resultaat.name} - {resultaat.description}\n")


def voorbeeld_1_profiel_aanmaken():
    """Voorbeeld 1: een profiel aanmaken uit een lijst punten."""
    kop("Voorbeeld 1: Een profiel aanmaken (default v4.0)")

    punten = [
        ProfielPunt(0.0, 2.3, 0.8),   # voorland
        ProfielPunt(50.0, 2.5, 0.8),  # teen: laatste voorlandpunt en eerste dijkpunt
        ProfielPunt(53.0, 3.0, 0.8),  # talud
        ProfielPunt(60.0, 3.2, 0.7),  # berm
        ProfielPunt(65.0, 7.0, 0.7),  # talud tot de kruin
    ]
    profiel = Profiel.from_punten(
        punten,
        voorland=2,
        id="TEST001",
        damtype=DamType.GEEN,
        damhoogte=0.0,
        richting=45.0,
        kruinhoogte=8.0,
        damwand=Damwandmodule.GEEN,
        memo="Aangemaakt test profiel",
    )
    toon_profiel(profiel)
    return profiel


def voorbeeld_2_versie_3_lezen():
    """Voorbeeld 2: een profiel in het formaat van versie 3 lezen."""
    kop("Voorbeeld 2: Een versie 3.0 profiel lezen uit een string")
    profiel = Profiel.from_string(PROFIEL_V3)
    toon_profiel(profiel)
    return profiel


def voorbeeld_3_versie_4_lezen():
    """Voorbeeld 3: een profiel in het formaat van versie 4 lezen."""
    kop("Voorbeeld 3: Een versie 4.0 profiel lezen uit een string")
    profiel = Profiel.from_string(PROFIEL_V4)
    toon_profiel(profiel)
    return profiel


def voorbeeld_4_opslaan_en_omzetten():
    """Voorbeeld 4: een versie 3 profiel opslaan als versie 4 en weer inlezen."""
    kop("Voorbeeld 4: Opslaan als versie 4 en weer inlezen")
    profiel = Profiel.from_string(PROFIEL_V3)
    profiel.id = "OMGEZET_V3"  # versie 3 kent geen ID

    with tempfile.TemporaryDirectory() as map_:
        pad = Path(map_) / "omgezet.prfl"
        profiel.save(pad, ProfielVersion.VERSION_4)
        print(f"Opgeslagen als versie 4:\n\n{pad.read_text(encoding='utf-8')}\n")
        ingelezen = Profiel.from_file(pad)

    gelijk = ingelezen.profiel_punten == profiel.profiel_punten
    print(f"Ingelezen: {ingelezen}")
    print(f"Zelfde punten als het origineel: {gelijk}\n")
    return ingelezen


def voorbeeld_5_fouten():
    """Voorbeeld 5: wat de controle meldt bij een ongeldig profiel of onleesbare invoer."""
    kop("Voorbeeld 5: Ongeldige profielen")

    # Het laatste dijkdeel heeft helling 1:10: te steil voor een berm, te flauw voor een talud
    te_flauw = Profiel.from_punten(
        [ProfielPunt(0.0, 2.0, 0.8), ProfielPunt(6.0, 3.0, 0.8), ProfielPunt(16.0, 4.0, 0.8)],
        kruinhoogte=6.0,
    )
    resultaat = te_flauw.check()
    print(f"Helling 1:10 op de dijk -> {resultaat.name} (code {resultaat.code}): {resultaat.description}")

    # Een regel die niet gelezen kan worden; de module logt een waarschuwing
    onleesbaar = Profiel.from_string(PROFIEL_V4.replace("6.000 3.000 0.8", "6.000 drie 0.8"))
    resultaat = onleesbaar.check()
    print(f"Onleesbare regel     -> {resultaat.name}: {onleesbaar.invoerfouten[0]}\n")
    return te_flauw, onleesbaar


def main():
    print("\n" + "=" * 60)
    print("ProfielCheckPython Module - Voorbeelden")
    print("=" * 60 + "\n")

    voorbeeld_1_profiel_aanmaken()
    voorbeeld_2_versie_3_lezen()
    voorbeeld_3_versie_4_lezen()
    voorbeeld_4_opslaan_en_omzetten()
    voorbeeld_5_fouten()

    print("=" * 60)
    print("Alle voorbeelden voltooid!")
    print("=" * 60)


if __name__ == "__main__":
    main()
