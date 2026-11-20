"""Tests for the joint-based StudInterface (anchors + RigidJoints)."""

import pytest

from cadbuildr.foundation import Assembly
from cadbuildr.foundation.dag_utils import show_dag
from cadbuildr.foundation.math_utils import tf_relative_to_frame

from cadbuildr_projects.lego import (
    LEGO_DIMENSIONS,
    LegoBrick,
    LegoFort,
    LegoRow,
    MatrixLegoArt,
    StudInterface,
)

PITCH = LEGO_DIMENSIONS.stud_pitch
HEIGHT = LEGO_DIMENSIONS.brick_height


def test_brick_has_mating_anchors():
    brick = LegoBrick(2, 2)
    assert brick.anchor("top").frame.position[2] == pytest.approx(HEIGHT)
    assert brick.anchor("bottom").frame.position[2] == pytest.approx(0.0)
    assert brick.anchor("seat").frame.position[2] == pytest.approx(0.0)


def test_on_top_of_stacks_one_level_up():
    assembly = Assembly()
    studs = StudInterface(assembly)
    base = studs.ground(LegoBrick(2, 2))
    top = studs.on_top_of(LegoBrick(2, 2))

    t_base, _ = tf_relative_to_frame(base.frame, assembly.frame)
    t_top, _ = tf_relative_to_frame(top.frame, assembly.frame)
    assert t_base == pytest.approx([0, 0, 0])
    assert t_top == pytest.approx([0, 0, HEIGHT])


def test_on_top_of_with_stud_offset():
    assembly = Assembly()
    studs = StudInterface(assembly)
    studs.ground(LegoBrick(4, 2))
    shifted = studs.on_top_of(LegoBrick(2, 2), at=(1, 0))
    t, _ = tf_relative_to_frame(shifted.frame, assembly.frame)
    assert t == pytest.approx([PITCH, 0, HEIGHT])


def test_tower_chained_on_top_of():
    assembly = Assembly()
    studs = StudInterface(assembly)
    studs.ground(LegoBrick(2, 2))
    bricks = [studs.on_top_of(LegoBrick(2, 2)) for _ in range(4)]
    t, _ = tf_relative_to_frame(bricks[-1].frame, assembly.frame)
    assert t == pytest.approx([0, 0, 4 * HEIGHT])
    assert len(assembly.joints) == 5  # 1 ground + 4 stacking joints


def test_beside_places_at_same_level():
    assembly = Assembly()
    studs = StudInterface(assembly)
    studs.ground(LegoBrick(4, 2))
    neighbour = studs.beside(LegoBrick(4, 2), at=(4, 0))
    t, _ = tf_relative_to_frame(neighbour.frame, assembly.frame)
    assert t == pytest.approx([4 * PITCH, 0, 0])


def test_explicit_base_with_of():
    assembly = Assembly()
    studs = StudInterface(assembly)
    base = studs.ground(LegoBrick(2, 2))
    studs.on_top_of(LegoBrick(2, 2))
    # place relative to the original base, not the last brick
    side = studs.beside(LegoBrick(2, 2), of=base, at=(2, 0))
    t, _ = tf_relative_to_frame(side.frame, assembly.frame)
    assert t == pytest.approx([2 * PITCH, 0, 0])


def test_ground_required_before_relative_placement():
    assembly = Assembly()
    studs = StudInterface(assembly)
    with pytest.raises(ValueError, match="No base brick"):
        studs.on_top_of(LegoBrick(2, 2))


def test_lego_row_on_joints_matches_grid_positions():
    row = LegoRow(brick_dim="4x2", axis="x", count=3)
    assert len(row.components) == 3
    xs = sorted(c.frame.position[0] for c in row.components)
    assert xs == pytest.approx([0.0, 4 * PITCH, 8 * PITCH])
    assert all(c.frame.position[2] == pytest.approx(0.0) for c in row.components)
    # Joint provenance is serialized on the assembly
    assert len(row.joints) == 3


def test_fresh_rows_place_identically_and_serialize_joints():
    # Full dag equality across builds is defeated by the global paint material
    # counter and across serializations by sketch-element accumulation (both
    # pre-existing foundation behaviors) — joint placement itself must be
    # reproducible, and joints must appear in the serialized assembly root.
    rows = [
        LegoRow(brick_dim="2x2", axis="y", count=2, colors=["bright_red"])
        for _ in range(2)
    ]
    positions = [[v for c in row.components for v in c.frame.position] for row in rows]
    assert positions[0] == pytest.approx(positions[1])

    dag = show_dag(rows[0])
    root = dag["DAG"][dag["rootNodeId"]]
    assert len(root["deps"].get("joints", [])) == 2
    assert "RigidJoint" in dag["serializableNodes"]


def test_place_grounds_first_brick_at_grid_origin_then_joints_the_rest():
    assembly = Assembly()
    studs = StudInterface(assembly, grid_origin=(-10.0, 5.0, -1.0))
    first = studs.place(LegoBrick(2, 2), at=(2, 0, 0))
    upper = studs.place(LegoBrick(2, 2), at=(0, 3, 2))
    t_first, _ = tf_relative_to_frame(first.frame, assembly.frame)
    t_upper, _ = tf_relative_to_frame(upper.frame, assembly.frame)
    assert t_first == pytest.approx([-10.0 + 2 * PITCH, 5.0, -1.0])
    assert t_upper == pytest.approx([-10.0, 5.0 + 3 * PITCH, -1.0 + 2 * HEIGHT])
    assert len(assembly.joints) == 2  # 1 ground + 1 grid joint


def test_fort_is_joint_placed_without_assembly_translate():
    fort = LegoFort(n_length_studs=8, n_width_studs=8, n_layers=2)
    assert fort.frame.position == pytest.approx([0.0, 0.0, 0.0])
    assert len(fort.joints) == len(fort.components)
    zs = sorted({round(c.frame.position[2], 6) for c in fort.components})
    assert zs == pytest.approx([-HEIGHT, 0.0])  # 2 layers centered on z=0


def test_pixel_art_top_is_centered_by_grid_origin():
    art = MatrixLegoArt([["bright_red", "white"], [None, "black"]], block_size_studs=1)
    assert art.frame.position == pytest.approx([0.0, 0.0, 0.0])
    assert len(art.joints) == len(art.components) == 3
    xs = sorted({c.frame.position[0] for c in art.components})
    assert xs == pytest.approx([-PITCH, 0.0])
    assert all(
        c.frame.position[2] == pytest.approx(-LEGO_DIMENSIONS.plate_height / 2)
        for c in art.components
    )
