"""
Conversie tussen tekst en getallen
Converted from ConvertString.cs
Copyright © 2016, 2017 HKV Services (original C# code)
Copyright © 2025-2026 HKV lijn in water B.V. (Python code)
Licensed under the EUPL
SPDX-License-Identifier: EUPL-1.2
Author: Rolf Waterman
Co-authors: Mario van den Berg, Claude

De conversie is bewust onafhankelijk van de locale: een punt én een komma
worden als decimaalteken geaccepteerd, en er wordt altijd met een punt geschreven.
"""

import math


def parse_float(text_in):
    """
    Converteer een tekst naar een float.

    Args:
        text_in: De te converteren tekst, met een punt of komma als decimaalteken

    Returns:
        De waarde als float

    Raises:
        ValueError: als de tekst geen getal is
    """
    return float(text_in.strip().replace(",", "."))


def parse_int(text_in):
    """
    Converteer een tekst naar een geheel getal ("3" en "3.0" zijn beide geldig).

    Raises:
        ValueError: als de tekst geen geheel getal is
    """
    value = parse_float(text_in)
    if not value.is_integer():
        raise ValueError(f"Geen geheel getal: {text_in!r}")
    return int(value)


def format_float(value_in):
    """
    Schrijf een getal met een punt als decimaalteken.

    NaN wordt geschreven als "NaN", zodat het met parse_float weer ingelezen kan worden.
    """
    value = float(value_in)
    if math.isnan(value):
        return "NaN"
    return repr(value)
