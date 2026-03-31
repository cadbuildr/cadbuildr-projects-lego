"""Interface helpers to place LEGO components on stud grids."""

from __future__ import annotations

from cadbuildr.foundation import AssemblyInterface, InterfaceGridSpec

from .constants import LEGO_DIMENSIONS


class LegoInterface:
    """Small wrapper around schema-generated AssemblyInterface."""

    def __init__(self):
        self.interface = AssemblyInterface(
            grid=InterfaceGridSpec(
                pitch_x=LEGO_DIMENSIONS.stud_pitch,
                pitch_y=LEGO_DIMENSIONS.stud_pitch,
                pitch_z=LEGO_DIMENSIONS.brick_height,
            )
        )

    def place(self, component, n_x: int = 0, n_y: int = 0, n_z: int = 0) -> bool:
        return bool(self.interface.place(component, n_x, n_y, n_z))

    def clip(self, component, n_x: int = 0, n_y: int = 0, n_z: int = 1) -> bool:
        return bool(self.interface.clip(component, n_x, n_y, n_z))

    def stick(self, component, position: str, offset_studs: int = 0) -> bool:
        """Relative stick helper for cardinal placement around origin."""
        if position == "left":
            return self.place(component, n_x=-offset_studs, n_y=0, n_z=0)
        if position == "right":
            return self.place(component, n_x=offset_studs, n_y=0, n_z=0)
        if position == "front":
            return self.place(component, n_x=0, n_y=-offset_studs, n_z=0)
        if position == "back":
            return self.place(component, n_x=0, n_y=offset_studs, n_z=0)
        raise ValueError(
            f"Unknown position '{position}'. Expected one of left/right/front/back."
        )

    def apply(self, assembly) -> bool:
        return bool(self.interface.apply(assembly))
