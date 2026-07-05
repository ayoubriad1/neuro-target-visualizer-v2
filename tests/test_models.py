from config import KCAL_MAX, KCAL_MIN
from models import RegionEntry, kcal_to_normalized, make_region_entry, strength_label


def test_kcal_to_normalized_bounds():
    assert kcal_to_normalized(KCAL_MAX) == 0.0
    assert kcal_to_normalized(KCAL_MIN) == 100.0


def test_kcal_to_normalized_clamps_out_of_range():
    assert kcal_to_normalized(0.0) == kcal_to_normalized(KCAL_MAX)
    assert kcal_to_normalized(-100.0) == kcal_to_normalized(KCAL_MIN)


def test_kcal_to_normalized_midpoint():
    mid = (KCAL_MIN + KCAL_MAX) / 2
    assert abs(kcal_to_normalized(mid) - 50.0) < 1e-9


def test_make_region_entry():
    entry = make_region_entry("Thalamus", -7.0)
    assert isinstance(entry, RegionEntry)
    assert entry.name == "Thalamus"
    assert entry.kcal == -7.0
    assert entry.normalized_intensity == kcal_to_normalized(-7.0)


def _contrast_ratio(hex1: str, hex2: str) -> float:
    def to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def linearize(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def luminance(rgb):
        r, g, b = (linearize(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1, l2 = luminance(to_rgb(hex1)), luminance(to_rgb(hex2))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def test_strength_label_meets_wcag_aa_contrast():
    # Regression guard: each (background, text) pair used for the strength
    # badges must clear WCAG AA (4.5:1) for small bold text - it's easy to
    # accidentally reintroduce a low-contrast color when tweaking the palette.
    for norm in (10.0, 30.0, 60.0, 90.0):
        label, bg, text = strength_label(norm)
        ratio = _contrast_ratio(bg, text)
        assert ratio >= 4.5, f"{label} ({bg} on {text}) contrast={ratio:.2f} < 4.5"
