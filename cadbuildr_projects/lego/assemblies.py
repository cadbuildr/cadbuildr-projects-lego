"""Common LEGO assembly compositions."""

from __future__ import annotations

import random

from cadbuildr.foundation import Assembly

from .brick import LegoBrick
from .constants import DEFAULT_LEGO_PALETTE, LEGO_DIMENSIONS
from .interface import LegoInterface


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
        interface = LegoInterface()

        for idx in range(count):
            brick = LegoBrick(n_length=n_length, n_width=n_width, color=random.choice(palette))
            x_studs = idx * n_length if axis == "x" else 0
            y_studs = idx * n_width if axis == "y" else 0
            interface.place(brick, n_x=x_studs, n_y=y_studs, n_z=0)

        interface.apply(self)


def _fort_place_corners(
    interface: LegoInterface,
    n_length: int,
    n_width: int,
    z: int,
    color: str,
) -> None:
    for nx, ny in (
        (0, 0),
        (n_length - 2, 0),
        (0, n_width - 2),
        (n_length - 2, n_width - 2),
    ):
        interface.place(LegoBrick(2, 2, short_height=True, color=color), n_x=nx, n_y=ny, n_z=z)


def _fort_fill_horizontal(
    interface: LegoInterface,
    x0: int,
    x1: int,
    y: int,
    z: int,
    phase: int,
    color: str,
) -> None:
    """Bonded run of 4x2 (+ 2x2 remainder) along x on [x0, x1) (stud indices)."""
    x = x0 + phase
    while x + 4 <= x1:
        interface.place(LegoBrick(4, 2, short_height=True, color=color), n_x=x, n_y=y, n_z=z)
        x += 4
    if x + 2 <= x1:
        interface.place(LegoBrick(2, 2, short_height=True, color=color), n_x=x, n_y=y, n_z=z)


def _fort_fill_vertical(
    interface: LegoInterface,
    y0: int,
    y1: int,
    x: int,
    z: int,
    phase: int,
    color: str,
) -> None:
    """Bonded run of 2x4 (+ 2x2 remainder) along y on [y0, y1)."""
    y = y0 + phase
    while y + 4 <= y1:
        interface.place(LegoBrick(2, 4, short_height=True, color=color), n_x=x, n_y=y, n_z=z)
        y += 4
    if y + 2 <= y1:
        interface.place(LegoBrick(2, 2, short_height=True, color=color), n_x=x, n_y=y, n_z=z)


class LegoFort(Assembly):
    """Perimeter fort with identical bonded walls on four sides (running bond) and shared corners."""

    def __init__(
        self,
        n_length_studs: int = 16,
        n_width_studs: int = 16,
        n_layers: int = 3,
        color: str = "bright_orange",
    ):
        super().__init__()
        if n_length_studs < 8 or n_width_studs < 8:
            raise ValueError("Fort footprint should be at least 8x8 studs.")
        if n_layers < 1:
            raise ValueError("n_layers must be >= 1")
        self.n_length_studs = n_length_studs
        self.n_width_studs = n_width_studs
        self.n_layers = n_layers
        self._build(color)

    def _build(self, color: str) -> None:
        interface = LegoInterface()
        ln, wd = self.n_length_studs, self.n_width_studs
        inner_x0, inner_x1 = 2, ln - 2
        inner_y0, inner_y1 = 2, wd - 2

        for layer in range(self.n_layers):
            phase = 2 if layer % 2 else 0
            _fort_place_corners(interface, ln, wd, layer, color)
            _fort_fill_horizontal(interface, inner_x0, inner_x1, 0, layer, phase, color)
            _fort_fill_horizontal(interface, inner_x0, inner_x1, wd - 2, layer, phase, color)
            _fort_fill_vertical(interface, inner_y0, inner_y1, 0, layer, phase, color)
            _fort_fill_vertical(interface, inner_y0, inner_y1, ln - 2, layer, phase, color)

        interface.apply(self)

        pitch = LEGO_DIMENSIONS.stud_pitch
        plate_h = LEGO_DIMENSIONS.plate_height
        self.translate(
            [
                -ln * pitch / 2.0,
                -wd * pitch / 2.0,
                -self.n_layers * plate_h / 2.0,
            ]
        )
