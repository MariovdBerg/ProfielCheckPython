# Changelog

All notable changes to ProfielCheckPython are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and from
version 2.0.0 onwards this project uses [Semantic Versioning](https://semver.org/).

ProfielCheckPython is a conversion of the C# library `daas.fn` 1.0.1.0 by Rolf Waterman
(HKV Services, 2016, 2017). The changes below are described relative to that C# code.
A first Python conversion (2025) was an intermediate step and was not released separately;
its own deviations from the C# code are listed at the end of the 2.0.0 section.

## [2.0.0] - 2026-10-19

### API: from C# to Python

| C# (`daas.fn`) | Python 2.0.0 |
|---|---|
| Namespace `daas.fn` | Package `prflcheck` (folder `src/prflcheck/`): `from prflcheck import Profiel` |
| `new Profiel(profielData)`, `new Profiel(naam, profielData)` | `Profiel.from_string(text)` or `Profiel.from_file(path)` |
| `new Profiel(id, damtype, damhoogte, richting, kruinhoogte, voorland, damwandmodule, memo, profielpunten)` | `Profiel.from_punten(punten, voorland=..., id=..., damtype=..., damwand=..., ...)` |
| `profiel.Controleer()` | `profiel.check()` |
| `ProfielError.Geen` | `ProfielError.OK` |
| `ProfielError.Error101` (integer value 3) | `ProfielError.ERROR101` (`.code` is 101) |
| `error.Caption()` | `error.description` |
| `profiel.Save(version, filePath)` | `profiel.save(file_path, version)`; `profiel.to_string(version)` for the text |
| `ProfielPunten` | `voorland_punten` and `dijk_punten`; `profiel_punten` is derived from them |
| `ProfielDelen`, `ProfieldelenFromProfielpunten()` | `profiel_delen`, always derived from the current points |
| `Voorland`, `Dijk` (settable, recalculated when reading) | `voorland`, `dijk` (read-only counts) |
| `ConvertString.ToDouble()`, `ToInt32()`, `DoubleToPoint()`, ... | `parse_float()`, `parse_int()`, `format_float()` |
| `DamType.SteileWand`, `Damwandmodule.DamwandPlusNeus`, ... | `DamType.STEILE_WAND`, `Damwandmodule.DAMWAND_PLUS_NEUS`, ... |
| `Log` (StringBuilder), `Debug.WriteLine`, `Console.WriteLine` | Python `logging` for warnings; no other output |
| `ProfielCheck`, `EnumeratorExtensions` | Removed (`ProfielCheck` was not used by `Controleer()`) |
| `Controleer_()` (unused alternative check) | Not converted |

### Fixed (bugs in the C# code)

- **NaN was written as `.a.`.** `DoubleToPoint(NaN)` gave "NaN", in which `ToPoint()`
  replaced every `N` by a decimal point. A missing value is now written as `NaN` and can
  be read back.
- **`Save(4, path)` did not write a file.** `SaveAsVersion4()` built the text but never
  wrote it. `save(path, 4)` now writes the file.
- **A memo with `{` or `}` made saving fail**, because the memo was used as a format string.
- **A missing crest height passed validation**, because a comparison with NaN is always
  false. A NaN kruinhoogte now gives ERROR122 (or ERROR130 for a dam wall with a foreland).
- **Numbers with a sign could not be read.** In `+3.5` the `+` was taken as the decimal
  separator.
- **A line with three values that are not all numbers raised an exception**, for example a
  typo in a point or an ID with spaces (`ID dijkvak 12`). An ID with spaces is now read
  correctly, and an unreadable line is reported (see *Added*).
- **Version 3:** the line `0.000 0.000 0.000` was written in the current culture, so as
  `0,000 0,000 0,000` with Dutch settings.
- **Version 3:** the last point was written with the roughness of the last section instead
  of its own roughness.
- **Gap between "berm" and ERROR116.** `TANAFLW` was 0.0667 while berms were counted up to
  1/15 (0.066667): a slope in between was neither a berm nor an error. `TANAFLW` is now 1/15;
  berms are still counted with a separate constant `TANABERM` = 1/15.
- ERROR113 message said "minder dan 2 meter"; the limit is 0.1 m.
- ERROR801 message said "damtype"; it is about the dam wall module.

### Added

- **Roughness check, ERROR121:** the roughness of each dike section must be between 0.5
  and 1.0. The C# code had the constants `RUWHEIDLAAG` and `RUWHEIDHOOG`, but did not use
  them, and had no error code 121.
- **INVOER is now used.** The C# code defined `ProfielError.Invoer` but never returned it.
  Lines that cannot be read are logged and stored in `Profiel.invoerfouten`, and `check()`
  returns INVOER. This includes points with more or fewer than 3 values, non-integer counts,
  a VOORLAND or DIJK count that does not match the number of points (v4), points outside
  the VOORLAND and DIJK sections (v4), and a VOORLAND larger than the number of points.
- **Reading and writing files:** `Profiel.from_file()` / `read_file()` (the C# code only read
  strings), with UTF-8 (with or without BOM) and a fallback to cp1252 with a warning.
  `to_string()` / `write_string()` give the text of both versions.
- If the `VERSIE` line is missing, the format is detected from the `DIJK` section
  (the C# code then treated the profile as version 3).
- Test suite with pytest (256 tests, 100% branch coverage), including boundary tests for
  every validation limit and round-trip tests for v3 and v4. Linting with ruff.
- `example_usage.py`, README, this changelog, and `LICENSE` (EUPL-1.2).

### Changed

- **License:** the C# code was "All Rights Reserved". The Python code is
  © 2025-2026 HKV lijn in water B.V., licensed under the EUPL-1.2.
- **Number parsing** accepts a point or a comma as decimal separator, as in C#, but no longer
  depends on the culture/locale settings.
- **A profile without a dike section and without a dam wall gives INVOER**, because it is not
  a dike profile. This applies to a profile of only one point (C#: ERROR105, the 2025
  conversion: OK) and to a profile with only a foreland (C#: ERROR119, the 2025
  conversion: OK). With a dam wall, such profiles are still allowed.
- `save()` writes version 4 by default and raises `ValueError` for an unknown version
  (C#: an unknown version was written as version 3).
- Unknown keywords are skipped with a warning. Lines starting with `#` (comments, skipped
  silently in C#) are also skipped with a warning.
- Memo: each line ends with a newline and trailing spaces are removed (C#: lines joined
  without a final newline).
- `str(ProfielDeel)` has a different layout.

### Validation results that differ from the C# code

These differences were introduced by the 2025 Python conversion. They have been reviewed
and are kept on purpose in 2.0.0.

| Situation | C# `Controleer()` | Python 2.0.0 |
|---|---|---|
| Profile with a dam wall (DAMWAND 1 or 2) | Dike sections are not checked (111-122 skipped) | All dike checks are done |
| Dam wall without foreland | Crest height compared with 0: ERROR130 if kruinhoogte <= 0 | No ERROR130 check |
| `from_punten(..., voorland=1)` | No foreland | INVOER |
| Version 3: first point line | Always skipped | Only skipped if it is `0 0 0` |
| Two dike points with the same x | ERROR113 | ERROR111 |
| Two dike points with the same z | ERROR115 | ERROR112 |
| Two foreland points with the same x | ERROR103 | ERROR101 |
| Several errors in the foreland | Checks all rules per section, first section first | Checks each rule for all sections, ERROR101 first |

### Fixed in the 2025 Python conversion (not present in C#)

The first Python conversion introduced these bugs; they are fixed in 2.0.0 and behave as
in C# again:

- Every version 4 file failed with ERROR111: the dike toe, written twice in v4, was
  counted twice. The C# code skipped this zero-length section.
- A version 3 file without foreland (`VOORLAND 1`) gave INVOER.
- An invalid dam type or dam wall module raised an exception or was silently replaced by
  `GEEN`, instead of giving ERROR800 or ERROR801.
- Reading numbers failed with a Dutch locale.

## [1.0.1.0] - 2017

C# library `daas.fn` for .NET Framework by Rolf Waterman, © HKV Services 2016, 2017:
`Profiel.cs`, `ProfielPunt.cs`, `ProfielDeel.cs`, `ProfielCheck.cs`, `ProfielEnums.cs`,
`ConvertString.cs` and `EnumeratorExtensions.cs`. Reads and writes Hydra/Ringtoets profiles
(version 3 and 4) and validates them with `Controleer()`.
