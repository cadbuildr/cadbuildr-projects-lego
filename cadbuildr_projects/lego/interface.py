"""Interface helpers to place LEGO components on stud grids."""

from __future__ import annotations

from collections.abc import Sequence

from cadbuildr.foundation import BoolParameter, RigidJoint

from .constants import LEGO_DIMENSIONS


class StudInterface:
    """Anchor/joint-based LEGO placement (foundation ``Anchor`` + ``RigidJoint``).

    Bricks snap by their stud grid without any transform math::

        assembly = Assembly()
        studs = StudInterface(assembly)
        base = studs.ground(LegoBrick(4, 2))
        studs.on_top_of(LegoBrick(2, 2), at=(1, 0))   # one stud over, one level up
        studs.beside(LegoBrick(4, 2), at=(4, 0))      # same level, 4 studs along x

    ``at`` offsets are integer stud counts between brick centers. When ``of``
    is omitted the last placed brick is the base.

    For layouts computed on an absolute grid (pixel art, walls), use
    :meth:`place` with ``(n_x, n_y, n_z)`` cells — ``n_z`` counts brick
    heights. Grid cell ``(0, 0, 0)`` sits at ``grid_origin`` (mm, assembly
    frame); the first placed brick is grounded there and every other brick
    is jointed to it, so re-centering a model is just a ``grid_origin``.
    """

    def __init__(self, assembly, grid_origin: Sequence[float] = (0.0, 0.0, 0.0)):
        self.assembly = assembly
        self.grid_origin = [float(v) for v in grid_origin]
        self._last = None
        self._grid_ref = None  # (brick, cell) of the grounded grid reference

    def _base(self, of):
        base = of if of is not None else self._last
        if base is None:
            raise ValueError(
                "No base brick placed yet: call ground(brick) first or pass of=<brick>."
            )
        return base

    def _stud_offset(self, anchor, at, label, levels=0):
        n_x, n_y = at
        if (n_x, n_y, levels) == (0, 0, 0):
            return anchor
        pitch = LEGO_DIMENSIONS.stud_pitch
        suffix = f"_{levels}" if levels else ""
        return anchor.offset(
            [n_x * pitch, n_y * pitch, levels * LEGO_DIMENSIONS.brick_height],
            name=f"{label}_{n_x}_{n_y}{suffix}",
        )

    def ground(self, brick, at: Sequence[float] = (0.0, 0.0, 0.0)):
        """Fix the first brick with its base center at ``at`` (mm, assembly frame)."""
        seat = brick.anchor("seat")
        if any(at):
            # Grounding the brick's seat shifted by -at puts the seat itself at
            # +at. TODO(foundation 0.2.17): self.assembly.ground(seat, at=at).
            seat = seat.offset([-float(v) for v in at], name="grounded_seat")
        self.assembly.ground(seat)
        self._last = brick
        return brick

    def place(self, brick, at: Sequence[int] = (0, 0, 0)):
        """Place ``brick`` on the absolute stud grid at cell ``(n_x, n_y, n_z)``.

        Brick centers land on ``grid_origin + (n_x, n_y) * pitch`` with the
        base at ``n_z`` brick heights; studs up, no rotation.
        """
        n_x, n_y, n_z = (int(v) for v in at)
        if self._grid_ref is None:
            pitch = LEGO_DIMENSIONS.stud_pitch
            height = LEGO_DIMENSIONS.brick_height
            ox, oy, oz = self.grid_origin
            self.ground(
                brick, at=(ox + n_x * pitch, oy + n_y * pitch, oz + n_z * height)
            )
            self._grid_ref = (brick, (n_x, n_y, n_z))
            return brick
        ref, (r_x, r_y, r_z) = self._grid_ref
        return self.beside(brick, of=ref, at=(n_x - r_x, n_y - r_y), levels=n_z - r_z)

    def on_top_of(self, brick, of=None, at=(0, 0)):
        """Clip ``brick`` onto the studs of a base brick, ``at`` studs over."""
        base = self._base(of)
        parent = self._stud_offset(base.anchor("top"), at, "at")
        self.assembly.add_joint(
            RigidJoint(parent_anchor=parent, child_anchor=brick.anchor("bottom"))
        )
        self._last = brick
        return brick

    def beside(self, brick, of=None, at=(1, 0), levels: int = 0):
        """Place ``brick`` at the base's level (``levels`` brick heights up),
        ``at`` studs over."""
        base = self._base(of)
        parent = self._stud_offset(base.anchor("seat"), at, "beside", levels)
        self.assembly.add_joint(
            RigidJoint(
                parent_anchor=parent,
                child_anchor=brick.anchor("seat"),
                flip=BoolParameter(value=False),
            )
        )
        self._last = brick
        return brick
