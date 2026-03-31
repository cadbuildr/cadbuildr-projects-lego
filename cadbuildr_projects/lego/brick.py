"""LEGO-like parametric brick."""

from __future__ import annotations

import random

from cadbuildr.foundation import Circle, Extrusion, Part, Point, Rectangle, Sketch

from .constants import DEFAULT_LEGO_PALETTE, LEGO_DIMENSIONS


class LegoBrick(Part):
    def __init__(
        self,
        n_length: int = 2,
        n_width: int = 2,
        short_height: bool = False,
        color: str | None = None,
    ):
        super().__init__()
        if n_length < 1 or n_width < 1:
            raise ValueError("LegoBrick dimensions must be >= 1 stud.")

        self.n_length = n_length
        self.n_width = n_width
        self.brick_length_mm = n_length * LEGO_DIMENSIONS.stud_pitch - LEGO_DIMENSIONS.clearance
        self.brick_width_mm = n_width * LEGO_DIMENSIONS.stud_pitch - LEGO_DIMENSIONS.clearance
        self.brick_height_mm = (
            LEGO_DIMENSIONS.plate_height if short_height else LEGO_DIMENSIONS.brick_height
        )

        self._build_outer_shell()
        self._build_inner_cavity()
        self._build_top_studs()
        self._build_inner_tubes()

        if color is None:
            color = random.choice(DEFAULT_LEGO_PALETTE)
        self.paint(color)

    def _build_outer_shell(self) -> None:
        sketch = Sketch(self.xy())
        square = Rectangle.from_center_and_sides(
            sketch.origin, self.brick_length_mm, self.brick_width_mm
        )
        self.add_operation(Extrusion(square, self.brick_height_mm))

    def _build_inner_cavity(self) -> None:
        inner_length = self.brick_length_mm - 2 * LEGO_DIMENSIONS.wall_thickness
        inner_width = self.brick_width_mm - 2 * LEGO_DIMENSIONS.wall_thickness
        if inner_length <= 0.0 or inner_width <= 0.0:
            return
        sketch = Sketch(self.xy())
        cavity = Rectangle.from_center_and_sides(sketch.origin, inner_length, inner_width)
        cut_depth = self.brick_height_mm - (
            LEGO_DIMENSIONS.stud_height - LEGO_DIMENSIONS.clearance
        )
        self.add_operation(Extrusion(cavity, cut_depth, cut=True))

    def _build_top_studs(self) -> None:
        sketch = Sketch(self.xy())
        x0 = -self.brick_length_mm / 2.0 + LEGO_DIMENSIONS.stud_pitch / 2.0
        y0 = -self.brick_width_mm / 2.0 + LEGO_DIMENSIONS.stud_pitch / 2.0
        for i in range(self.n_length):
            for j in range(self.n_width):
                center = Point(
                    sketch,
                    x0 + i * LEGO_DIMENSIONS.stud_pitch,
                    y0 + j * LEGO_DIMENSIONS.stud_pitch,
                )
                stud = Circle(center, LEGO_DIMENSIONS.stud_diameter / 2.0)
                self.add_operation(
                    Extrusion(
                        stud,
                        self.brick_height_mm,
                        self.brick_height_mm + LEGO_DIMENSIONS.stud_height,
                    )
                )

    def _build_inner_tubes(self) -> None:
        sketch = Sketch(self.xy())
        x0 = -self.brick_length_mm / 2.0 + LEGO_DIMENSIONS.stud_pitch / 2.0
        y0 = -self.brick_width_mm / 2.0 + LEGO_DIMENSIONS.stud_pitch / 2.0
        for i in range(self.n_length):
            for j in range(self.n_width):
                center = Point(
                    sketch,
                    x0 + i * LEGO_DIMENSIONS.stud_pitch,
                    y0 + j * LEGO_DIMENSIONS.stud_pitch,
                )
                tube = Circle(center, LEGO_DIMENSIONS.tube_diameter / 2.0)
                self.add_operation(
                    Extrusion(tube, LEGO_DIMENSIONS.stud_height, self.brick_height_mm)
                )
