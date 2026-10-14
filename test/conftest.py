from pathlib import Path

import pytest

from src import ProfielPunt

TESTPROFILES_DIR = Path(__file__).parent / "testprofiles"


def fixture_path(filename):
    return TESTPROFILES_DIR / filename


def punten(*coordinaten, r=0.8):
    """Maak ProfielPunten uit (x, z)-paren."""
    return [ProfielPunt(x, z, r) for x, z in coordinaten]


@pytest.fixture
def geldig_dijk_punten():
    """Een dijk zonder voorland die alle controles doorstaat (talud - berm - talud)."""
    return punten((0.0, 0.0), (4.0, 2.0), (24.0, 3.0), (28.0, 5.0))
