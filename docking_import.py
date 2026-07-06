"""Parsers for importing docking results instead of manual re-entry.

Two supported inputs:
- CSV/TSV bulk import: one row per region, `region,kcal` columns (+ optional
  `x,y,z` for the exact-coordinate advanced mode). Lets a researcher paste in
  an entire batch of docking results at once instead of clicking "Add Region"
  by hand, N times - the single biggest friction point for anyone with a
  real virtual-screening output to visualize. Optional `pdb_id`, `protein`
  (or `gene`) and `ligand` columns let the same sheet also carry which PDB
  structure and which docked molecule each score came from - pure provenance
  metadata (not used by the renderer), so a multi-protein x multi-ligand
  screening batch stays traceable in one place instead of split across
  several notes. See gene_region.py for why a missing region can't just be
  auto-filled from `protein`/`gene` - RCSB has no anatomical field to draw
  that from (see rcsb_lookup.py), so this only *suggests* candidates in the
  error message.
- A single AutoDock Vina result file (a `.pdbqt` output, or the plain-text
  log Vina prints to stdout/a log file): extracts the best (most negative)
  binding affinity score, so it doesn't have to be retyped by hand. A Vina
  score is for one ligand-target pair with no inherent brain-region
  association, so the user still has to pick which region/receptor this
  score belongs to - this only saves the copy/retype step, not that
  scientific judgment call.
"""
import csv
import io
import re
from dataclasses import dataclass, field

from brain_regions import get_region_names
from gene_region import suggest_regions


@dataclass(frozen=True)
class ImportedRow:
    name: str
    kcal: float
    coordinates: tuple[float, float, float] | None = None
    # Provenance-only metadata (not used by the renderer) - see module docstring.
    pdb_id: str | None = None
    protein: str | None = None
    ligand: str | None = None


@dataclass(frozen=True)
class CSVImportResult:
    rows: list[ImportedRow] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)  # one human-readable message per bad row


def _missing_region_message(protein: str | None) -> str:
    """The base "missing region" error, plus a hand-curated region suggestion
    when the row's `protein`/`gene` column matches a known receptor target
    (see gene_region.py) - a hint, never an auto-pick, so the row still gets
    skipped and the user still has to add a `region` value themselves.
    """
    base = "missing region name (and no x/y/z given)"
    if not protein:
        return f"{base}."
    candidates = suggest_regions(protein)
    if not candidates:
        return f"{base} - '{protein}' isn't in this app's gene/receptor lookup table."
    return (
        f"{base} - '{protein}' is typically associated with: "
        f"{', '.join(candidates)} (pick one and add it to the region column; "
        "this tool does not auto-assign a region for a receptor's score)."
    )


def parse_csv(text: str) -> CSVImportResult:
    """Parses `region,kcal` (+ optional `x,y,z`) rows. The header is
    case-insensitive and column-order-independent (`kcal`/`kcal_mol`/
    `affinity` and `region`/`name` are all accepted spellings). A row with
    `x`,`y`,`z` all present uses the exact-coordinate advanced mode (matching
    the sidebar), with `region` optional in that case - a blank region name
    falls back to the same auto-generated "Custom (x, y, z)" label the
    sidebar uses. Malformed or unrecognized rows are skipped and reported in
    `.errors` rather than silently dropped or crashing the whole import.
    """
    rows: list[ImportedRow] = []
    errors: list[str] = []
    known_names = set(get_region_names())

    reader = csv.DictReader(io.StringIO(text.strip()))
    if not reader.fieldnames:
        return CSVImportResult(rows, ["Empty file - no header row found."])
    fieldmap = {f.strip().lower(): f for f in reader.fieldnames if f}

    kcal_key = fieldmap.get("kcal") or fieldmap.get("kcal_mol") or fieldmap.get("affinity")
    if kcal_key is None:
        return CSVImportResult(rows, [
            "No affinity column found - expected a header named 'kcal', "
            "'kcal_mol', or 'affinity'."
        ])
    region_key = fieldmap.get("region") or fieldmap.get("name")
    x_key, y_key, z_key = fieldmap.get("x"), fieldmap.get("y"), fieldmap.get("z")
    pdb_key = fieldmap.get("pdb_id") or fieldmap.get("pdb")
    protein_key = fieldmap.get("protein") or fieldmap.get("gene")
    ligand_key = fieldmap.get("ligand") or fieldmap.get("molecule") or fieldmap.get("compound")

    for line_num, row in enumerate(reader, start=2):  # header occupies line 1
        raw_kcal = (row.get(kcal_key) or "").strip()
        try:
            kcal = float(raw_kcal)
        except ValueError:
            errors.append(f"Line {line_num}: could not parse affinity value '{raw_kcal}'.")
            continue
        if kcal >= 0:
            errors.append(
                f"Line {line_num}: affinity {kcal} must be negative (kcal/mol - "
                "more negative means stronger binding)."
            )
            continue

        coordinates = None
        if x_key and y_key and z_key and row.get(x_key) and row.get(y_key) and row.get(z_key):
            try:
                coordinates = (float(row[x_key]), float(row[y_key]), float(row[z_key]))
            except ValueError:
                errors.append(f"Line {line_num}: could not parse x/y/z coordinates.")
                continue

        pdb_id = (row.get(pdb_key) or "").strip() or None if pdb_key else None
        protein = (row.get(protein_key) or "").strip() or None if protein_key else None
        ligand = (row.get(ligand_key) or "").strip() or None if ligand_key else None

        raw_region = (row.get(region_key) or "").strip() if region_key else ""
        if coordinates is not None:
            name = raw_region or (
                f"Custom ({coordinates[0]:.0f}, {coordinates[1]:.0f}, {coordinates[2]:.0f})"
            )
        elif not raw_region:
            errors.append(f"Line {line_num}: {_missing_region_message(protein)}")
            continue
        elif raw_region not in known_names:
            errors.append(
                f"Line {line_num}: unknown region '{raw_region}' - not one of this app's "
                "atlas regions, and no x/y/z columns given to use exact-coordinate mode instead."
            )
            continue
        else:
            name = raw_region

        rows.append(ImportedRow(
            name=name, kcal=kcal, coordinates=coordinates,
            pdb_id=pdb_id, protein=protein, ligand=ligand,
        ))

    return CSVImportResult(rows, errors)


# Vina's PDBQT pose output: "REMARK VINA RESULT:   -8.3      0.000      0.000"
_VINA_REMARK_RE = re.compile(r"REMARK VINA RESULT:\s*(-?\d+\.?\d*)")
# Vina's plain-text results table:
#    mode |   affinity | dist from best mode
#         | (kcal/mol) | rmsd l.b.| rmsd u.b.
#    -----+------------+----------+----------
#       1       -8.3      0.000      0.000
_VINA_LOG_ROW_RE = re.compile(r"^\s*\d+\s+(-?\d+\.\d+)\s", re.MULTILINE)


def parse_vina_score(text: str) -> float | None:
    """Extracts the best (first/top-ranked pose = most favourable) binding
    affinity from either a Vina PDBQT output file (REMARK VINA RESULT lines)
    or Vina's plain-text log/stdout results table. Returns None if neither
    pattern is found, so the caller can tell the user the file wasn't
    recognized instead of silently importing nothing.
    """
    remark_matches = _VINA_REMARK_RE.findall(text)
    if remark_matches:
        return float(remark_matches[0])
    log_matches = _VINA_LOG_ROW_RE.findall(text)
    if log_matches:
        return float(log_matches[0])
    return None
