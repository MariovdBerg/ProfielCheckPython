"""
Example usage of the daas_fn Python module
"""

from src import Profiel, ProfielPunt


def example_1_create_from_scratch():
    """Example 1: Create a profile from scratch"""
    print("=" * 60)
    print("Voorbeeld 1: Een profiel aanmaken (default v4.0)")
    print("=" * 60)

    # Create profile points
    punten = [
        ProfielPunt(0.0, 2.3, 0.8),
        ProfielPunt(50.0, 2.5, 0.8),
        ProfielPunt(53.0, 3.0, 0.8),
        ProfielPunt(60.0, 3.2, 0.7),
        ProfielPunt(65.0, 7.0, 0.7),
    ]

    # Create profile
    profiel = Profiel.from_punten(
        punten,
        voorland=2,
        id="TEST001",
        damtype=0,
        damhoogte=0.0,
        richting=45.0,
        kruinhoogte=8.0,
        damwand=0,
        memo="Aangemaakt test profiel",
    )

    print(f"Versie: {profiel.versie}")
    print(f"Profiel ID: {profiel.id}")
    print(f"Richting: {profiel.richting}")
    print(f"Dam type: {profiel.damtype.name}")
    print(f"Dam hoogte: {profiel.damhoogte}")
    print(f"Voorlandpunten: {profiel.voorland}")
    print(f"Kruinhoogte: {profiel.kruinhoogte}")
    print(f"Damwand: {profiel.damwand.name}")
    print(f"Dijkpunten: {profiel.dijk}")
    print(f"Profielpunten: {len(profiel.profiel_punten)}")
    print(f"Memo: {profiel.memo.strip()}")

    # Display profile sections
    print("\nProfiel delen:")
    for i, deel in enumerate(profiel.profiel_delen):
        print(f"  {i + 1}. {deel}")
    print()

    # Validate the profile
    result = profiel.check()
    print(f"Profiel validatie: {result.name} - {result.description}")
    print()


def example_2_parse_v3_from_string():
    """Example 2: Parse a profile from string data"""
    print("=" * 60)
    print("Voorbeeld 2: Maak een versie 3.0 profiel via een string")
    print("=" * 60)

    profile_data = """VERSIE	3.0
    DAM		0
    DAMHOOGTE	0.0
    RICHTING	90.0
    KRUINHOOGTE	8.5
    VOORLAND	3
    DAMWAND		0
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

    profiel = Profiel.from_string(profile_data)

    print(f"Versie: {profiel.versie}")
    print(f"Dam type: {profiel.damtype.name}")
    print(f"Dam hoogte: {profiel.damhoogte}")
    print(f"Richting: {profiel.richting}")
    print(f"Kruinhoogte: {profiel.kruinhoogte}")
    print(f"Voorlandpunten: {profiel.voorland}")
    print(f"Damwand: {profiel.damwand.name}")
    print(f"Profielpunten: {len(profiel.profiel_punten)}")
    print(f"Memo: {profiel.memo.strip()}")

    # Display profile sections
    print("\nProfiel delen:")
    for i, deel in enumerate(profiel.profiel_delen):
        print(f"  {i+1}. {deel}")

    # Validate
    result = profiel.check()
    print(f"\nValidatie: {result.name} - {result.description}")
    print()


def example_3_parse_v4_from_string():
    """Example 3: Parse a v4 profile from string data"""
    print("=" * 60)
    print("Voorbeeld 3: Maak een versie 4.0 profiel via een string")
    print("=" * 60)

    profile_data = """VERSIE 4.0
    ID TEST0004
    
    RICHTING 90.0
    
    DAM 0
    DAMHOOGTE 0.0
    
    VOORLAND 2
    -50.000	1.000	0.8
    0.000	2.000	0.8
    
    KRUINHOOGTE 8.5
    
    DAMWAND 0
    DIJK 6
    0.000	2.000	0.8
    15.000	2.500	0.8
    30.000	3.000	0.8
    35.000	5.000	0.7
    40.000	7.500	0.7
    45.000	8.000	0.7
    
    MEMO
    Dit is een test profiel gemaakt met een string.
    """

    profiel = Profiel.from_string(profile_data)

    print(f"Versie: {profiel.versie}")
    print(f"Profiel ID: {profiel.id}")
    print(f"Richting: {profiel.richting}")
    print(f"Dam type: {profiel.damtype.name}")
    print(f"Dam hoogte: {profiel.damhoogte}")
    print(f"Voorlandpunten: {profiel.voorland}")
    print(f"Damwand: {profiel.damwand.name}")
    print(f"Kruinhoogte: {profiel.kruinhoogte}")
    print(f"Dijkpunten: {profiel.dijk}")
    print(f"Profielpunten: {len(profiel.profiel_punten)}")
    print(f"Memo: {profiel.memo.strip()}")

    # Display profile sections
    print("\nProfiel delen:")
    for i, deel in enumerate(profiel.profiel_delen):
        print(f"  {i + 1}. {deel}")

    # Validate
    result = profiel.check()
    print(f"\nValidatie: {result.name} - {result.description}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ProfielCheckPython Module - Voorbeelden")
    print("=" * 60 + "\n")

    example_1_create_from_scratch()
    example_2_parse_v3_from_string()
    example_3_parse_v4_from_string()

    print("=" * 60)
    print("Alle voorbeelden voltooid!")
    print("=" * 60)
