# Changelog

All notable changes to this project are documented in this file.

## 0.2.0 - unreleased

- Bricks expose mating anchors `top`, `bottom`, `seat`; new `StudInterface`
  places bricks with foundation `RigidJoint`s (`ground`, `on_top_of`, `beside`,
  `place` on an absolute stud grid with `grid_origin`).
- `LegoFort`, `MatrixLegoArt` / `build_lego_matrix` and `LegoRow` are joint-placed;
  no more assembly translate for centering. Brick poses are unchanged.
- **Breaking:** removed the grid-translation `LegoInterface`.
- Parametric `@cadbuildr_project` entry points (`lego_brick`, `lego_fort`,
  `matrix_lego_art`) with emitted parameter schemas.
- Requires `cadbuildr-foundation ^0.2.16`.

## 0.1.0 - 2026-03-30

- Initial sync from the monorepo for `cadbuildr_projects/lego`.
- Added package metadata, source modules, examples, and lockfile.
- Added repository `.gitignore` for local/build/cache artifacts.
