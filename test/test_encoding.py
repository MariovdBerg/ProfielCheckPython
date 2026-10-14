import logging

import pytest

from src import Profiel, ProfielError, read_file
from src.reader import VERVANGTEKEN

TEKST = "VERSIE 4.0\nID X\nVOORLAND 0\nKRUINHOOGTE 8.0\nDIJK 2\n0 2 0.8\n8 3 0.8\nMEMO\nDijk bij Één, café\n"


def schrijf(tmp_path, data):
    pad = tmp_path / "profiel.prfl"
    pad.write_bytes(data)
    return pad


def test_utf8_geeft_geen_waarschuwing(tmp_path, caplog):
    pad = schrijf(tmp_path, TEKST.encode("utf-8"))
    with caplog.at_level(logging.WARNING):
        profiel = read_file(pad)
    assert caplog.records == []
    assert profiel.memo == "Dijk bij Één, café\n"
    assert profiel.check() == ProfielError.OK


def test_utf8_met_bom(tmp_path, caplog):
    """Een BOM mag de eerste regel (VERSIE) niet onherkenbaar maken."""
    pad = schrijf(tmp_path, TEKST.encode("utf-8-sig"))
    with caplog.at_level(logging.WARNING):
        profiel = read_file(pad)
    assert caplog.records == []
    assert profiel.versie == 4.0
    assert profiel.id == "X"


def test_cp1252_geeft_waarschuwing_en_wordt_toch_gelezen(tmp_path, caplog):
    pad = schrijf(tmp_path, TEKST.encode("cp1252"))
    with caplog.at_level(logging.WARNING):
        profiel = Profiel.from_file(pad)
    assert profiel.memo == "Dijk bij Één, café\n"
    assert profiel.check() == ProfielError.OK
    assert len(caplog.records) == 1
    melding = caplog.records[0].getMessage()
    assert "geen geldig UTF-8" in melding
    assert "regel 9" in melding
    assert "0xC9" in melding  # 'É' in cp1252
    assert "cp1252" in melding
    assert str(pad) in melding


def test_bytes_die_ook_in_cp1252_niet_bestaan(tmp_path, caplog):
    data = TEKST.encode("utf-8").replace("café".encode(), b"caf" + bytes([0x81]))
    pad = schrijf(tmp_path, data)
    with caplog.at_level(logging.WARNING):
        profiel = read_file(pad)
    assert profiel.memo.endswith("caf" + VERVANGTEKEN + "\n")
    assert len(caplog.records) == 2
    assert "vervangen" in caplog.records[1].getMessage()


def test_opgegeven_codering_geeft_geen_waarschuwing(tmp_path, caplog):
    pad = schrijf(tmp_path, TEKST.encode("cp1252"))
    with caplog.at_level(logging.WARNING):
        profiel = read_file(pad, encoding="cp1252")
    assert caplog.records == []
    assert profiel.memo == "Dijk bij Één, café\n"


def test_opgegeven_utf8_is_strikt(tmp_path):
    pad = schrijf(tmp_path, TEKST.encode("cp1252"))
    with pytest.raises(UnicodeDecodeError):
        read_file(pad, encoding="utf-8")


def test_save_en_from_file_met_codering(tmp_path):
    profiel = Profiel.from_string(TEKST)
    pad = tmp_path / "uit.prfl"
    profiel.save(pad, encoding="cp1252")
    assert Profiel.from_file(pad, encoding="cp1252").memo == profiel.memo
