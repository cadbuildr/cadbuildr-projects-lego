"""LEGO-inspired primitives and assembly builders for CADbuildr projects."""

from .constants import LEGO_DIMENSIONS, LEGO_STORE_COLORS, DEFAULT_LEGO_PALETTE
from .brick import LegoBrick
from .interface import StudInterface
from .assemblies import LegoRow, LegoFort
from .pixel_art import MatrixLegoArt, build_lego_matrix
from .cadbuildr_code_logo import (
    CADBUILDR_CODE_LOGO_BRAND_HEX_B,
    CADBUILDR_CODE_LOGO_BRAND_HEX_O,
    CADBUILDR_CODE_LOGO_COMPACT,
    CADBUILDR_CODE_LOGO_MATRIX,
    matrix_from_cadbuildr_code_logo_compact,
)

# `projects` uses the `cadbuildr_project` decorator + parameter descriptors
# (Color/Int/Enum) added to ``cadbuildr-foundation`` in the SDK rollout. Older
# published foundations (pre-0.2.8) do not expose those symbols, in which case
# the rest of the package (LegoBrick, LegoFort, ...) must still be importable.
# Make the decorated entry points best-effort so the github-io Pyodide bootstrap
# survives pinned-foundation environments until the new wheel is published.
try:
    from .projects import lego_brick, lego_fort, matrix_lego_art
except ImportError:
    lego_brick = lego_fort = matrix_lego_art = None  # type: ignore[assignment]

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
    "StudInterface",
    "LegoRow",
    "LegoFort",
    "MatrixLegoArt",
    "build_lego_matrix",
    "CADBUILDR_CODE_LOGO_BRAND_HEX_B",
    "CADBUILDR_CODE_LOGO_BRAND_HEX_O",
    "CADBUILDR_CODE_LOGO_COMPACT",
    "CADBUILDR_CODE_LOGO_MATRIX",
    "matrix_from_cadbuildr_code_logo_compact",
    "lego_brick",
    "lego_fort",
    "matrix_lego_art",
]
