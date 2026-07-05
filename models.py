"""Typed data model for a selected brain region + affinity, replacing the
original bare (name, kcal, normalized) positional tuple.
"""
from dataclasses import dataclass

from config import KCAL_MAX, KCAL_MIN


@dataclass(frozen=True)
class RegionEntry:
    name: str
    kcal: float
    normalized_intensity: float  # 0-100, see kcal_to_normalized()


def kcal_to_normalized(kcal: float) -> float:
    clamped = max(KCAL_MIN, min(KCAL_MAX, kcal))
    return (abs(clamped) - abs(KCAL_MAX)) / (abs(KCAL_MIN) - abs(KCAL_MAX)) * 100.0


def make_region_entry(name: str, kcal: float) -> RegionEntry:
    return RegionEntry(name=name, kcal=kcal, normalized_intensity=kcal_to_normalized(kcal))


def strength_label(norm: float) -> tuple[str, str, str]:
    """(label, background color, text color) for a normalized intensity -
    shared by the sidebar region chips and the main affinity summary cards so
    both use the same strength bands and colors. Each (background, text)
    pair is chosen to clear WCAG AA contrast (>= 4.5:1) for small bold text -
    "Strong"/"Moderate" are slightly darkened from their original hue, and
    "Weak" pairs with dark instead of white text, rather than just picking
    colors that look nice and hoping they're legible.
    """
    if norm >= 75:
        return "Very strong", "#6E5BB5", "#FFFFFF"
    if norm >= 50:
        return "Strong", "#8164C0", "#FFFFFF"
    if norm >= 25:
        return "Moderate", "#9C5BBC", "#FFFFFF"
    return "Weak", "#C9A7DE", "#2D2A3A"
