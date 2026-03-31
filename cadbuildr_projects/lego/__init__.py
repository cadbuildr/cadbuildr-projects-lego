"""LEGO-inspired primitives and assembly builders for CADbuildr projects."""

from .constants import LEGO_DIMENSIONS, LEGO_STORE_COLORS, DEFAULT_LEGO_PALETTE
from .brick import LegoBrick
from .interface import LegoInterface
from .assemblies import LegoRow, LegoFort
from .pixel_art import MatrixLegoArt, build_lego_matrix

# Short aliases for a cleaner public API.
Beam = LegoBrick
Plate = LegoBrick

__all__ = [
    "LEGO_DIMENSIONS",
    "LEGO_STORE_COLORS",
    "DEFAULT_LEGO_PALETTE",
    "Beam",
    "Plate",
    "LegoBrick",
    "LegoInterface",
    "LegoRow",
    "LegoFort",
    "MatrixLegoArt",
    "build_lego_matrix",
]
