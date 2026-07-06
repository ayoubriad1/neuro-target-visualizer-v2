"""Save/load a full analysis session (region list + receptor weighting
choice) as JSON, so a researcher can persist, resume, or hand off a specific
analysis to a colleague without a screenshot - loading the same JSON back
into this app reproduces the exact same rendered map, since the rendering
is a pure function of these inputs.

Deliberately excludes anything session-only or credential-like: the AI
provider/API key are never serialized, matching this app's existing
BYOK/never-persisted-elsewhere posture for those fields.
"""
import json
from dataclasses import dataclass, field

from brain_regions import get_region_names
from models import RegionEntry, make_region_entry
from receptor_atlas import RECEPTOR_NAMES

_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SessionImportResult:
    regions: list[RegionEntry] = field(default_factory=list)
    receptor_weight: str | None = None
    errors: list[str] = field(default_factory=list)


def export_session(regions: list[RegionEntry], receptor_weight: str | None) -> str:
    """A small, human-readable JSON document - deliberately simple enough to
    hand-edit or generate from another script, not just round-trip through
    this app's own UI.
    """
    payload = {
        "version": _SCHEMA_VERSION,
        "receptor_weight": receptor_weight,
        "regions": [
            {
                "name": r.name,
                "kcal": r.kcal,
                "coordinates": list(r.coordinates) if r.coordinates is not None else None,
            }
            for r in regions
        ],
    }
    return json.dumps(payload, indent=2)


def import_session(text: str) -> SessionImportResult:
    """Parses a session JSON document. Each malformed/unrecognized region
    entry is reported individually and skipped - one bad entry never
    discards an otherwise-valid session - matching docking_import.parse_csv's
    partial-success behavior. An unrecognized `receptor_weight` is reported
    and dropped (falls back to no weighting) rather than failing the import.
    """
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        return SessionImportResult(errors=[f"Invalid JSON: {e}"])
    if not isinstance(payload, dict):
        return SessionImportResult(errors=["Expected a JSON object at the top level."])

    known_names = set(get_region_names())
    errors: list[str] = []
    regions: list[RegionEntry] = []

    raw_regions = payload.get("regions")
    if not isinstance(raw_regions, list):
        return SessionImportResult(errors=["Missing or invalid 'regions' list."])

    for i, raw in enumerate(raw_regions, start=1):
        if not isinstance(raw, dict):
            errors.append(f"Region {i}: expected a JSON object.")
            continue
        name = raw.get("name")
        kcal = raw.get("kcal")
        coords_raw = raw.get("coordinates")

        if not isinstance(name, str) or not name:
            errors.append(f"Region {i}: missing or invalid 'name'.")
            continue
        if not isinstance(kcal, int | float) or isinstance(kcal, bool) or kcal >= 0:
            errors.append(f"Region {i} ('{name}'): 'kcal' must be a negative number.")
            continue

        coordinates = None
        if coords_raw is not None:
            valid_shape = (
                isinstance(coords_raw, list) and len(coords_raw) == 3
                and all(isinstance(v, int | float) and not isinstance(v, bool) for v in coords_raw)
            )
            if not valid_shape:
                errors.append(f"Region {i} ('{name}'): 'coordinates' must be a [x, y, z] list of numbers.")
                continue
            coordinates = (float(coords_raw[0]), float(coords_raw[1]), float(coords_raw[2]))
        elif name not in known_names:
            errors.append(f"Region {i}: unknown region '{name}' and no coordinates given.")
            continue

        regions.append(make_region_entry(name, float(kcal), coordinates))

    receptor_weight = payload.get("receptor_weight")
    if receptor_weight is not None and receptor_weight not in RECEPTOR_NAMES:
        errors.append(f"Unknown receptor_weight '{receptor_weight}' - ignored.")
        receptor_weight = None

    return SessionImportResult(regions=regions, receptor_weight=receptor_weight, errors=errors)
