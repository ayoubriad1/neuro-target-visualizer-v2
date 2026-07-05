from atlas_regions import ATLAS_REGIONS
from brain_regions import BRAIN_REGIONS, get_coordinates, get_region_names


def test_region_names_sorted_and_nonempty():
    names = get_region_names()
    assert names == sorted(names)
    assert len(names) > 0
    # Every offered name must be explainable: either a real atlas mask, or an
    # illustrative fallback point - never neither.
    assert set(names) == set(BRAIN_REGIONS) | ATLAS_REGIONS


def test_illustrative_coordinates_are_xyz_triples_in_mni152_bounds():
    # BRAIN_REGIONS is currently empty (every region migrated to a real atlas
    # - see CHANGELOG.md), but this stays meaningful if an illustrative
    # fallback point is ever reintroduced for a region with no atlas.
    for name in BRAIN_REGIONS:
        coords = get_coordinates(name)
        assert len(coords) == 3
        assert all(isinstance(v, (int, float)) for v in coords)
        x, y, z = coords
        # MNI152 2mm template extent: x in [-90, 90], y in [-126, 90], z in [-72, 108]
        assert -90 <= x <= 90
        assert -126 <= y <= 90
        assert -72 <= z <= 108


def test_get_coordinates_only_defined_for_illustrative_regions():
    for name in ATLAS_REGIONS:
        assert name not in BRAIN_REGIONS, (
            f"{name} is atlas-backed but also has a stale illustrative point"
        )
