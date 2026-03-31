"""Common LEGO assembly compositions."""

from __future__ import annotations

import random

from cadbuildr.foundation import Assembly

from .brick import LegoBrick
from .constants import DEFAULT_LEGO_PALETTE
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


class LegoFort(Assembly):
    def __init__(self, n_length_studs: int = 16, n_width_studs: int = 16, n_layers: int = 3):
        super().__init__()
        if n_length_studs < 8 or n_width_studs < 8:
            raise ValueError("Fort footprint should be at least 8x8 studs.")
        if n_layers < 1:
            raise ValueError("n_layers must be >= 1")
        self.n_length_studs = n_length_studs
        self.n_width_studs = n_width_studs
        self.n_layers = n_layers
        self._build()

    def _build(self) -> None:
        interface = LegoInterface()
        x_count = max(1, self.n_length_studs // 4)
        y_count = max(1, self.n_width_studs // 4)

        for layer in range(self.n_layers):
            x_shift = 2 if layer % 2 else 0
            z = layer

            for i in range(x_count):
                x = i * 4 + x_shift
                if x + 4 > self.n_length_studs:
                    continue
                front = LegoBrick(4, 2)
                back = LegoBrick(4, 2)
                interface.place(front, n_x=x, n_y=0, n_z=z)
                interface.place(back, n_x=x, n_y=max(0, self.n_width_studs - 2), n_z=z)

            for j in range(y_count):
                y = j * 4
                if y + 4 > self.n_width_studs:
                    continue
                left = LegoBrick(2, 4)
                right = LegoBrick(2, 4)
                interface.place(left, n_x=0, n_y=y, n_z=z)
                interface.place(right, n_x=max(0, self.n_length_studs - 2), n_y=y, n_z=z)

        interface.apply(self)
