"""Parametric ``@cadbuildr_project`` entry points for the LEGO demo.

Each function wraps an existing LEGO assembly class with a typed parameter
schema. The schema is emitted to ``parameters/`` next to the package via
``cadbuildr_projects.lego.emit_schemas`` and consumed by the SDK auto-form
(T11) + the frozen-DAG runtime (T12).
"""

from __future__ import annotations

from cadbuildr.foundation import Color, Enum, Int, cadbuildr_project

from .assemblies import LegoFort
from .brick import LegoBrick
from .constants import LEGO_STORE_COLORS
from .pixel_art import MatrixLegoArt

LEGO_COLOR_CHOICES = tuple(sorted(LEGO_STORE_COLORS.keys()))


@cadbuildr_project(
    project_id="lego_brick",
    title="Single LEGO brick",
    description="One LEGO brick of the chosen footprint and color.",
    parameters=[
        Int("n_length", default=2, min=1, max=16, step=1, label="Length (studs)"),
        Int("n_width", default=2, min=1, max=16, step=1, label="Width (studs)"),
        Color("brick_color", default="bright_red", choices=LEGO_COLOR_CHOICES, label="Color"),
    ],
)
def lego_brick(n_length: int, n_width: int, brick_color: str) -> LegoBrick:
    return LegoBrick(n_length=n_length, n_width=n_width, color=brick_color)


@cadbuildr_project(
    project_id="lego_fort",
    title="Fortress perimeter",
    description="Four-walled fortress with running-bond bricks and shared corners.",
    parameters=[
        Int("n_length_studs", default=16, min=8, max=48, step=2, label="Footprint length"),
        Int("n_width_studs", default=16, min=8, max=48, step=2, label="Footprint width"),
        Int("n_layers", default=4, min=1, max=12, step=1, label="Wall layers"),
        Color(
            "brick_color",
            default="bright_red",
            choices=LEGO_COLOR_CHOICES,
            label="Brick color",
        ),
    ],
)
def lego_fort(
    n_length_studs: int,
    n_width_studs: int,
    n_layers: int,
    brick_color: str,
) -> LegoFort:
    return LegoFort(
        n_length_studs=n_length_studs,
        n_width_studs=n_width_studs,
        n_layers=n_layers,
        color=brick_color,
    )


@cadbuildr_project(
    project_id="matrix_lego_art",
    title="Matrix LEGO art",
    description=(
        "Pixel-art plate driven by a 2D matrix of color names. The matrix is supplied at"
        " render time; this project's tunable parameters are the per-pixel size and the"
        " fill color used as the empty-cell default."
    ),
    parameters=[
        Int("block_size_studs", default=2, min=1, max=4, step=1, label="Block size (studs)"),
        Color(
            "empty_color",
            default="black",
            choices=LEGO_COLOR_CHOICES,
            label="Empty-cell color",
        ),
        Enum(
            "fill_mode",
            default="solid",
            choices=("solid", "checker"),
            label="Fill mode",
            description="Solid uses the matrix verbatim; checker treats empty cells specially.",
        ),
    ],
)
def matrix_lego_art(
    block_size_studs: int,
    empty_color: str,
    fill_mode: str,
    matrix: list[list[str]] | None = None,
) -> MatrixLegoArt:
    """Build the matrix-art plate.

    The actual color grid is supplied at render time as the ``matrix`` argument
    (kept out of the parameter schema because the SDK auto-form does not yet
    surface 2D grid editors).
    """
    if matrix is None:
        matrix = [[empty_color]]
    if fill_mode == "checker":
        matrix = [
            [
                cell if (row_idx + col_idx) % 2 == 0 else empty_color
                for col_idx, cell in enumerate(row)
            ]
            for row_idx, row in enumerate(matrix)
        ]
    return MatrixLegoArt(matrix=matrix, block_size_studs=block_size_studs)
