"""Dimensions and color palette for LEGO-like modeling."""

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class LegoDimensions:
    stud_pitch: float = 8.0
    brick_height: float = 9.6
    plate_height: float = 3.2
    wall_thickness: float = 1.2
    stud_diameter: float = 4.8
    stud_height: float = 1.7
    tube_diameter: float = 2.6
    clearance: float = 0.2


LEGO_DIMENSIONS = LegoDimensions()

# Names map to colors registered in cadbuildr.foundation.constants.DEFAULT_COLORS.
LEGO_STORE_COLORS = {
    "bright_red": "bright_red",
    "bright_orange": "bright_orange",
    "bright_yellow": "bright_yellow",
    "bright_green": "bright_green",
    "bright_blue": "bright_blue",
    "medium_azure": "medium_azure",
    "lavender": "lavender",
    "coral": "coral",
    "white": "white",
    "black": "black",
    "tan": "tan",
    "light_bluish_gray": "light_bluish_gray",
    "dark_bluish_gray": "dark_bluish_gray",
    "reddish_brown": "reddish_brown",
}

# Standard LEGO-like palette with representative hex values.
LEGO_STANDARD_COLOR_HEX = {
    "bright_red": "#C91A09",
    "bright_orange": "#E76318",
    "bright_yellow": "#F2CD37",
    "bright_green": "#4B9F4A",
    "bright_blue": "#0055BF",
    "medium_azure": "#36AEBF",
    "lavender": "#A06EB9",
    "coral": "#FF6D77",
    "white": "#F4F4F4",
    "black": "#111111",
    "tan": "#DEC69C",
    "light_bluish_gray": "#A0A5A9",
    "dark_bluish_gray": "#6C6E68",
    "reddish_brown": "#582A12",
}

STANDARD_LEGO_COLORS = list(LEGO_STANDARD_COLOR_HEX.keys())

DEFAULT_LEGO_PALETTE = [
    LEGO_STORE_COLORS["bright_red"],
    LEGO_STORE_COLORS["bright_orange"],
    LEGO_STORE_COLORS["bright_yellow"],
    LEGO_STORE_COLORS["bright_green"],
    LEGO_STORE_COLORS["bright_blue"],
    LEGO_STORE_COLORS["medium_azure"],
    LEGO_STORE_COLORS["lavender"],
    LEGO_STORE_COLORS["white"],
]


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    token = hex_color.strip().lstrip("#")
    if len(token) != 6:
        raise ValueError(f"Invalid hex color '{hex_color}'. Expected #RRGGBB.")
    return int(token[0:2], 16), int(token[2:4], 16), int(token[4:6], 16)


def nearest_lego_color_from_hex(hex_color: str) -> str:
    """Map any hex color to the nearest standard LEGO color name."""
    target_r, target_g, target_b = _hex_to_rgb(hex_color)
    best_name = "bright_red"
    best_dist = float("inf")
    for name, palette_hex in LEGO_STANDARD_COLOR_HEX.items():
        r, g, b = _hex_to_rgb(palette_hex)
        dist = sqrt((target_r - r) ** 2 + (target_g - g) ** 2 + (target_b - b) ** 2)
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return LEGO_STORE_COLORS[best_name]
