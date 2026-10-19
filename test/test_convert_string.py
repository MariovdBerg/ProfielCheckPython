import locale
import math

import pytest

from prflcheck import format_float, parse_float, parse_int


@pytest.mark.parametrize("tekst, verwacht", [
    ("123.456", 123.456),
    ("123,456", 123.456),
    ("-45.67", -45.67),
    ("+3.5", 3.5),  # B3: '+' werd als decimaalteken gezien
    ("1e3", 1000.0),
    ("1.5e-2", 0.015),
    ("  7  ", 7.0),
    ("8", 8.0),
])
def test_parse_float(tekst, verwacht):
    assert parse_float(tekst) == pytest.approx(verwacht)


@pytest.mark.parametrize("tekst", ["", "abc", "1.234,5", "1,2,3"])
def test_parse_float_ongeldig(tekst):
    with pytest.raises(ValueError):
        parse_float(tekst)


def test_parse_float_nan():
    assert math.isnan(parse_float("NaN"))


def test_parse_float_onafhankelijk_van_locale(monkeypatch):
    """B6: met een Nederlandse locale (komma) moet '1.5' nog steeds 1.5 opleveren."""
    monkeypatch.setattr(locale, "localeconv", lambda: {"decimal_point": ","})
    assert parse_float("1.5") == 1.5
    assert parse_float("1,5") == 1.5


@pytest.mark.parametrize("tekst, verwacht", [("3", 3), ("3.0", 3), ("-2", -2), ("0", 0)])
def test_parse_int(tekst, verwacht):
    assert parse_int(tekst) == verwacht


@pytest.mark.parametrize("tekst", ["1.5", "NaN", "inf", "x"])
def test_parse_int_ongeldig(tekst):
    with pytest.raises(ValueError):
        parse_int(tekst)


@pytest.mark.parametrize("waarde, verwacht", [
    (123.456, "123.456"),
    (8, "8.0"),
    (-0.5, "-0.5"),
    (math.nan, "NaN"),  # B2: werd '.a.'
    (math.inf, "inf"),
])
def test_format_float(waarde, verwacht):
    assert format_float(waarde) == verwacht


@pytest.mark.parametrize("waarde", [0.1, 9.4, -1234.5678, 1e-7, math.inf, -math.inf])
def test_format_parse_round_trip(waarde):
    assert parse_float(format_float(waarde)) == waarde


def test_format_parse_round_trip_nan():
    assert math.isnan(parse_float(format_float(math.nan)))
