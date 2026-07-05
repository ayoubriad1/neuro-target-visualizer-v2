from brain_regions import BRAIN_REGIONS, get_coordinates, get_region_names


def test_region_names_sorted_and_nonempty():
    names = get_region_names()
    assert names == sorted(names)
    assert len(names) == len(BRAIN_REGIONS)


def test_all_coordinates_are_xyz_triples():
    for name in get_region_names():
        coords = get_coordinates(name)
        assert len(coords) == 3
        assert all(isinstance(v, (int, float)) for v in coords)


def test_coordinates_within_mni152_bounds():
    # MNI152 2mm template extent: x in [-90, 90], y in [-126, 90], z in [-72, 108]
    for name in get_region_names():
        x, y, z = get_coordinates(name)
        assert -90 <= x <= 90
        assert -126 <= y <= 90
        assert -72 <= z <= 108
