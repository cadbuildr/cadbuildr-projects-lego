"""Common LEGO assembly compositions."""

from __future__ import annotations

import random

from cadbuildr.foundation import Assembly

from .brick import LegoBrick
from .constants import DEFAULT_LEGO_PALETTE, LEGO_DIMENSIONS
from .interface import StudInterface


def _parse_brick_dim(brick_dim: str) -> tuple[int, int]:
    tokens = brick_dim.lower().split("x")
    if len(tokens) != 2:
        raise ValueError(f"Expected brick_dim as NxM, got '{brick_dim}'.")
    return int(tokens[0]), int(tokens[1])


class LegoRow(Assembly):
    def __init__(
        self,
        brick_dim: str = "4x2",
        axis: str = "x",
        count: int = 3,
        colors: list[str] | None = None,
    ):
        super().__init__()
        if count < 1:
            raise ValueError("count must be >= 1")
        if axis not in {"x", "y"}:
            raise ValueError("axis must be either 'x' or 'y'")

        n_length, n_width = _parse_brick_dim(brick_dim)
        palette = colors or DEFAULT_LEGO_PALETTE
        studs = StudInterface(self)
        step = (n_length, 0) if axis == "x" else (0, n_width)

        studs.ground(
            LegoBrick(n_length=n_length, n_width=n_width, color=random.choice(palette))
        )
        for _ in range(count - 1):
            brick = LegoBrick(
                n_length=n_length, n_width=n_width, color=random.choice(palette)
            )
            studs.beside(brick, at=step)


def _checker_color(palette: list[str], layer: int, seq_idx: int) -> str:
    """Checker palette pick: shifting by `layer` flips colors row-over-row so a wall
    viewed from the side reads as a grid (alternation in BOTH axes)."""
    return palette[(layer + seq_idx) % len(palette)]


def _fort_place(
    studs: StudInterface, n_l: int, n_w: int, x: int, y: int, z: int, color: str
) -> None:
    """Place an ``n_l`` x ``n_w`` brick whose min corner is stud cell ``(x, y)``.

    The fort layout is computed on brick corners; ``StudInterface.place`` takes
    brick centers, so shift by half the footprint (footprints are even).
    """
    studs.place(LegoBrick(n_l, n_w, color=color), at=(x + n_l // 2, y + n_w // 2, z))


def _fort_place_corners(
    studs: StudInterface,
    n_length: int,
    n_width: int,
    z: int,
    palette: list[str],
) -> None:
    # Corners are visited in a fixed order; checkering against `seq` keeps them
    # offset from their neighbours in the adjacent wall (which start at seq=0).
    for seq, (nx, ny) in enumerate(
        (
            (0, 0),
            (n_length - 2, 0),
            (0, n_width - 2),
            (n_length - 2, n_width - 2),
        )
    ):
        _fort_place(studs, 2, 2, nx, ny, z, _checker_color(palette, z, seq))


def _fort_fill_horizontal(
    studs: StudInterface,
    x0: int,
    x1: int,
    y: int,
    z: int,
    phase: int,
    palette: list[str],
) -> None:
    """Bonded run of 4x2 (+ 2x2 remainder) along x on [x0, x1) (stud indices)."""
    x = x0 + phase
    seq = 0
    while x + 4 <= x1:
        _fort_place(studs, 4, 2, x, y, z, _checker_color(palette, z, seq))
        x += 4
        seq += 1
    if x + 2 <= x1:
        _fort_place(studs, 2, 2, x, y, z, _checker_color(palette, z, seq))


def _fort_fill_vertical(
    studs: StudInterface,
    y0: int,
    y1: int,
    x: int,
    z: int,
    phase: int,
    palette: list[str],
) -> None:
    """Bonded run of 2x4 (+ 2x2 remainder) along y on [y0, y1)."""
    y = y0 + phase
    seq = 0
    while y + 4 <= y1:
        _fort_place(studs, 2, 4, x, y, z, _checker_color(palette, z, seq))
        y += 4
        seq += 1
    if y + 2 <= y1:
        _fort_place(studs, 2, 2, x, y, z, _checker_color(palette, z, seq))


class LegoFort(Assembly):
    """Perimeter fort with identical bonded walls on four sides (running bond) and shared corners.

    ``colors`` cycles per layer (e.g. ``["black", "bright_orange"]`` alternates courses).
    The legacy ``color=`` kwarg is still accepted for back-compat — it becomes a single-entry list.
    """

    def __init__(
        self,
        n_length_studs: int = 16,
        n_width_studs: int = 16,
        n_layers: int = 3,
        color: str | None = None,
        colors: list[str] | None = None,
    ):
        super().__init__()
        if n_length_studs < 8 or n_width_studs < 8:
            raise ValueError("Fort footprint should be at least 8x8 studs.")
        if n_layers < 1:
            raise ValueError("n_layers must be >= 1")
        self.n_length_studs = n_length_studs
        self.n_width_studs = n_width_studs
        self.n_layers = n_layers
        if colors is None:
            palette = [color] if color is not None else ["bright_orange"]
        else:
            if not colors:
                raise ValueError("colors must not be empty")
            palette = list(colors)
        self._build(palette)

    def _build(self, palette: list[str]) -> None:
        ln, wd = self.n_length_studs, self.n_width_studs
        pitch = LEGO_DIMENSIONS.stud_pitch
        # Grid cell (0, 0, 0) is offset so the fort sits around the origin.
        studs = StudInterface(
            self,
            grid_origin=(
                -ln * pitch / 2.0,
                -wd * pitch / 2.0,
                -self.n_layers * LEGO_DIMENSIONS.brick_height / 2.0,
            ),
        )
        inner_x0, inner_x1 = 2, ln - 2
        inner_y0, inner_y1 = 2, wd - 2

        for layer in range(self.n_layers):
            phase = 2 if layer % 2 else 0
            _fort_place_corners(studs, ln, wd, layer, palette)
            _fort_fill_horizontal(studs, inner_x0, inner_x1, 0, layer, phase, palette)
            _fort_fill_horizontal(
                studs, inner_x0, inner_x1, wd - 2, layer, phase, palette
            )
            _fort_fill_vertical(studs, inner_y0, inner_y1, 0, layer, phase, palette)
            _fort_fill_vertical(
                studs, inner_y0, inner_y1, ln - 2, layer, phase, palette
            )
