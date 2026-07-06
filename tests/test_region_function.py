from atlas_regions import ATLAS_REGIONS
from region_function import REGION_FUNCTION, get_functional_profile


def test_every_atlas_region_has_a_functional_profile():
    missing = ATLAS_REGIONS - set(REGION_FUNCTION)
    assert not missing, f"Missing functional profiles for: {missing}"


def test_every_profile_has_domains_description_effects_and_citation():
    for name, profile in REGION_FUNCTION.items():
        assert profile.domains, f"{name} has no domains"
        assert profile.description, f"{name} has no description"
        assert profile.stimulation_effect, f"{name} has no stimulation_effect"
        assert profile.inhibition_effect, f"{name} has no inhibition_effect"
        assert profile.citation, f"{name} has no citation"


def test_get_functional_profile_known_region():
    profile = get_functional_profile("Primary Motor Cortex")
    assert profile is not None
    assert "Motor / motricity" in profile.domains


def test_get_functional_profile_unknown_region_returns_none():
    assert get_functional_profile("Custom (0, 0, 0)") is None
    assert get_functional_profile("Not a real region") is None
