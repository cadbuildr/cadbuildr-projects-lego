"""Generic matrix-driven LEGO plate builders."""

from __future__ import annotations

from cadbuildr.foundation import Assembly

from .brick import LegoBrick
from .constants import LEGO_STORE_COLORS, nearest_lego_color_from_hex
from .interface import LegoInterface

ColorToken = str | None
ColorMatrix = list[list[ColorToken]]


def _resolve_color_token(color: str) -> str:
    if color.startswith("#"):
        return nearest_lego_color_from_hex(color)
    if color in LEGO_STORE_COLORS:
        return LEGO_STORE_COLORS[color]
    return color


def build_lego_matrix(
    assembly: Assembly,
    matrix: ColorMatrix,
    block_size_studs: int = 2,
    z_level: int = 0,
    orientation: str = "top",
    side_thickness_studs: int = 2,
) -> None:
    """Place LEGO bricks/plates from a top-left color matrix."""
    if block_size_studs < 1:
        raise ValueError("block_size_studs must be >= 1.")
    if side_thickness_studs < 1:
        raise ValueError("side_thickness_studs must be >= 1.")
    if orientation not in {"top", "side"}:
        raise ValueError("orientation must be 'top' or 'side'.")
    if not matrix:
        return

    width = max(len(row) for row in matrix)
    height = len(matrix)
    interface = LegoInterface()

    for y, row in enumerate(matrix):
        for x, color in enumerate(row):
            if color is None:
                continue
            if orientation == "top":
                piece = LegoBrick(
                    block_size_studs,
                    block_size_studs,
                    short_height=True,
                    color=_resolve_color_token(color),
                )
                interface.place(
                    piece,
                    n_x=x * block_size_studs,
                    n_y=(height - y - 1) * block_size_studs,
                    n_z=z_level,
                )
            else:
                piece = LegoBrick(
                    n_length=block_size_studs,
                    n_width=side_thickness_studs,
                    short_height=False,
                    color=_resolve_color_token(color),
                )
                interface.place(
                    piece,
                    n_x=x * block_size_studs,
                    n_y=0,
                    n_z=z_level + (height - y - 1),
                )
    interface.apply(assembly)

    # Attach dimensions to the assembly for easy introspection by callers.
    assembly.width = width
    assembly.height = height


class MatrixLegoArt(Assembly):
    """Generic LEGO art from a matrix."""

    def __init__(
        self,
        matrix: ColorMatrix,
        block_size_studs: int = 2,
        orientation: str = "top",
        side_thickness_studs: int = 2,
    ):
        super().__init__()
        build_lego_matrix(
            self,
            matrix=matrix,
            block_size_studs=block_size_studs,
            orientation=orientation,
            side_thickness_studs=side_thickness_studs,
        )
