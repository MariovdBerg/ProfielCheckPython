"""
Profiel reader
Converted from Profiel.cs (Lees)
Copyright © HKV Services 2016, 2017
Author: Rolf Waterman

Inlezen van profielen in het formaat van versie 3 en versie 4.

Versie 3: VOORLAND n gevolgd door één lijst punten; de eerste n punten zijn het voorland
          (n = 0 of 1: geen voorland). De eerste regel "0.000 0.000 0.000" wordt overgeslagen.
Versie 4: VOORLAND n gevolgd door de n voorlandpunten, DIJK m gevolgd door de m dijkpunten.
"""

import logging

from .convert_string import parse_float, parse_int
from .model import Profiel, ProfielPunt

logger = logging.getLogger(__name__)


# Profielen uit oudere (Windows-)programmatuur zijn vaak in deze codering opgeslagen
FALLBACK_ENCODING = "cp1252"
VERVANGTEKEN = chr(0xFFFD)  # Unicode-vervangteken voor bytes die niet te decoderen zijn


def read_file(file_path, encoding=None):
    """
    Lees een profiel uit een bestand.

    Args:
        file_path: Pad naar het bestand
        encoding: Codering van het bestand. Bij None wordt UTF-8 (met of zonder BOM) gebruikt;
            is het bestand geen geldig UTF-8, dan wordt het met een waarschuwing als cp1252 gelezen.
            Bij een opgegeven codering wordt alleen die gebruikt.
    """
    with open(file_path, "rb") as f:
        data = f.read()
    if encoding is not None:
        return read_string(data.decode(encoding))
    return read_string(_decodeer(data, file_path))


def _decodeer(data, bron):
    """Decodeer als UTF-8; val terug op cp1252 met een waarschuwing als dat niet lukt."""
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        regel = data[:e.start].count(b"\n") + 1
        logger.warning(
            "%s is geen geldig UTF-8 (regel %d, byte 0x%02X); het bestand wordt gelezen als %s. "
            "Controleer speciale tekens, bijvoorbeeld in het memo, of geef de codering op met encoding=...",
            bron, regel, data[e.start], FALLBACK_ENCODING)

    tekst = data.decode(FALLBACK_ENCODING, errors="replace")
    if VERVANGTEKEN in tekst:
        logger.warning("%s bevat tekens die ook in %s niet bestaan; deze zijn vervangen door %r.",
                       bron, FALLBACK_ENCODING, VERVANGTEKEN)
    return tekst


def read_string(profiel_data):
    """Lees een profiel uit een tekst."""
    return _Lezer().lees(profiel_data)


class _Lezer:
    """Leest een profieltekst regel voor regel."""

    def __init__(self):
        self.velden = {}
        self.versie = None
        self.aantal_voorland = 0
        self.aantal_dijk = None
        self.sectie = None  # None, "VOORLAND" of "DIJK": waar volgende punten bij horen
        self.punten = {None: [], "VOORLAND": [], "DIJK": []}
        self.alle_punten = []
        self.memo = []
        self.invoerfouten = []
        self._sleutelwoorden = {
            "VERSIE": self._versie,
            "ID": self._id,
            "DAM": self._dam,
            "DAMHOOGTE": self._float_veld("damhoogte"),
            "RICHTING": self._float_veld("richting"),
            "KRUINHOOGTE": self._float_veld("kruinhoogte"),
            "VOORLAND": self._voorland,
            "DAMWAND": self._damwand,
            "DIJK": self._dijk,
        }

    def lees(self, tekst):
        # Ondersteun ook teksten waarin regeleinden als letterlijke "\n" zijn opgeslagen
        tekst = tekst.replace("\\r\\n", "\n").replace("\\n", "\n")
        regels = tekst.splitlines()

        for nummer, regel in enumerate(regels, start=1):
            delen = regel.split()
            if not delen:
                continue
            sleutel = delen[0].upper()
            if sleutel == "MEMO":
                self.memo = [r.rstrip() for r in regels[nummer:] if r.strip()]
                break

            handler = self._sleutelwoorden.get(sleutel)
            try:
                if handler:
                    handler(regel, delen[1:])
                else:
                    self._punt_of_onbekend(regel, delen)
            except (ValueError, IndexError) as e:
                self._fout(nummer, regel, e)

        return self._maak_profiel()

    def _fout(self, nummer, regel, oorzaak):
        melding = f"Regel {nummer} kan niet worden gelezen: {regel.strip()!r} ({oorzaak})"
        logger.warning(melding)
        self.invoerfouten.append(melding)

    # --- sleutelwoorden -------------------------------------------------

    def _versie(self, regel, waarden):
        self.versie = parse_float(waarden[0])

    def _id(self, regel, waarden):
        self.velden["id"] = regel.split(maxsplit=1)[1].strip()

    def _dam(self, regel, waarden):
        self.velden["damtype"] = parse_int(waarden[-1])

    def _damwand(self, regel, waarden):
        self.velden["damwand"] = parse_int(waarden[-1])

    def _float_veld(self, naam):
        def lees_veld(regel, waarden):
            self.velden[naam] = parse_float(waarden[0])
        return lees_veld

    def _voorland(self, regel, waarden):
        self.sectie = "VOORLAND"
        self.aantal_voorland = parse_int(waarden[0])

    def _dijk(self, regel, waarden):
        self.sectie = "DIJK"
        self.aantal_dijk = parse_int(waarden[0])

    def _punt_of_onbekend(self, regel, delen):
        try:
            parse_float(delen[0])
        except ValueError:
            logger.warning("Onbekende regel overgeslagen: %r", regel.strip())
            return
        if len(delen) != 3:
            raise ValueError("een profielpunt bestaat uit X, Z en ruwheid")
        punt = ProfielPunt(*(parse_float(d) for d in delen))
        self.punten[self.sectie].append(punt)
        self.alle_punten.append(punt)

    # --- opbouw van het profiel -------------------------------------------

    def _maak_profiel(self):
        versie = self.versie
        if versie is None:
            # Zonder VERSIE-regel: herken versie 4 aan de DIJK-sectie
            versie = 4.0 if self.aantal_dijk is not None else 3.0

        if versie < 4:
            voorland_punten, dijk_punten = self._punten_versie_3()
        else:
            voorland_punten, dijk_punten = self._punten_versie_4()

        memo = "".join(regel + "\n" for regel in self.memo)
        return Profiel(versie=versie, voorland_punten=voorland_punten, dijk_punten=dijk_punten,
                       memo=memo, invoerfouten=self.invoerfouten, **self.velden)

    def _punten_versie_3(self):
        punten = self.alle_punten
        if punten and punten[0] == ProfielPunt(0.0, 0.0, 0.0):
            punten = punten[1:]

        n = self.aantal_voorland
        if n <= 1:
            # VOORLAND 1 is alleen de teen: geen voorland
            return [], punten
        if n > len(punten):
            self.invoerfouten.append(
                f"VOORLAND ({n}) is groter dan het aantal profielpunten ({len(punten)})")
        return punten[:n], punten[n - 1:]

    def _punten_versie_4(self):
        if self.punten[None]:
            self.invoerfouten.append("Er staan profielpunten buiten de secties VOORLAND en DIJK")
        voorland_punten = self.punten["VOORLAND"]
        dijk_punten = self.punten["DIJK"]
        if len(voorland_punten) != self.aantal_voorland:
            self.invoerfouten.append(
                f"VOORLAND {self.aantal_voorland} maar er staan {len(voorland_punten)} voorlandpunten")
        if self.aantal_dijk is not None and len(dijk_punten) != self.aantal_dijk:
            self.invoerfouten.append(
                f"DIJK {self.aantal_dijk} maar er staan {len(dijk_punten)} dijkpunten")
        return voorland_punten, dijk_punten
