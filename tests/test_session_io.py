import json

from models import make_region_entry
from session_io import export_session, import_session


def test_export_then_import_round_trips_exactly():
    regions = [
        make_region_entry("Thalamus", -9.2),
        make_region_entry("Custom (10, -20, 5)", -7.5, coordinates=(10.0, -20.0, 5.0)),
    ]
    text = export_session(regions, "D2 (dopamine receptor)")
    result = import_session(text)
    assert result.errors == []
    assert result.receptor_weight == "D2 (dopamine receptor)"
    assert len(result.regions) == 2
    assert result.regions[0].name == "Thalamus"
    assert result.regions[0].kcal == -9.2
    assert result.regions[0].coordinates is None
    assert result.regions[1].coordinates == (10.0, -20.0, 5.0)


def test_export_produces_readable_json():
    regions = [make_region_entry("Thalamus", -9.2)]
    text = export_session(regions, None)
    payload = json.loads(text)
    assert payload["version"] == 1
    assert payload["receptor_weight"] is None
    assert payload["regions"] == [{"name": "Thalamus", "kcal": -9.2, "coordinates": None}]


def test_import_invalid_json_reports_error():
    result = import_session("{not valid json")
    assert result.regions == []
    assert "Invalid JSON" in result.errors[0]


def test_import_missing_regions_key():
    result = import_session("{}")
    assert result.regions == []
    assert "regions" in result.errors[0]


def test_import_rejects_unknown_region_name():
    text = json.dumps({"version": 1, "receptor_weight": None,
                       "regions": [{"name": "Not A Real Region", "kcal": -9.0, "coordinates": None}]})
    result = import_session(text)
    assert result.regions == []
    assert "unknown region" in result.errors[0]


def test_import_rejects_positive_kcal():
    text = json.dumps({"regions": [{"name": "Thalamus", "kcal": 5.0, "coordinates": None}]})
    result = import_session(text)
    assert result.regions == []
    assert "must be a negative number" in result.errors[0]


def test_import_rejects_malformed_coordinates():
    text = json.dumps({"regions": [{"name": "Custom", "kcal": -9.0, "coordinates": [1.0, 2.0]}]})
    result = import_session(text)
    assert result.regions == []
    assert "coordinates" in result.errors[0]


def test_import_partial_success_keeps_good_rows():
    text = json.dumps({"regions": [
        {"name": "Thalamus", "kcal": -9.0, "coordinates": None},
        {"name": "Not A Real Region", "kcal": -3.0, "coordinates": None},
    ]})
    result = import_session(text)
    assert len(result.regions) == 1
    assert result.regions[0].name == "Thalamus"
    assert len(result.errors) == 1


def test_import_unknown_receptor_weight_is_dropped_not_fatal():
    text = json.dumps({
        "regions": [{"name": "Thalamus", "kcal": -9.0, "coordinates": None}],
        "receptor_weight": "Not A Real Receptor",
    })
    result = import_session(text)
    assert len(result.regions) == 1
    assert result.receptor_weight is None
    assert any("receptor_weight" in e for e in result.errors)


def test_import_no_receptor_weight_key_defaults_to_none():
    text = json.dumps({"regions": [{"name": "Thalamus", "kcal": -9.0, "coordinates": None}]})
    result = import_session(text)
    assert result.receptor_weight is None
    assert result.errors == []


def test_import_rejects_non_object_top_level():
    result = import_session("[1, 2, 3]")
    assert result.regions == []
    assert "JSON object" in result.errors[0]


def test_import_rejects_boolean_kcal():
    # bool is a subclass of int in Python - must not slip through the
    # numeric-kcal check as if it were a real number.
    text = json.dumps({"regions": [{"name": "Thalamus", "kcal": True, "coordinates": None}]})
    result = import_session(text)
    assert result.regions == []
    assert "must be a negative number" in result.errors[0]
