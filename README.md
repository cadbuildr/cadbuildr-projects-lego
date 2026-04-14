# cadbuildr_projects.lego

## Summary

LEGO-inspired primitives and assembly builders in the `cadbuildr_projects` namespace.

## Tags

cad, python, lego, assembly

## Dependencies

### Upstream

- cadbuildr-foundation

### Downstream

- (none)

## GitHub Pages demo (Vite + R3F)

Static browser demo for `kernel-api` + Pyodide lives next to this package:

`github-io/` — from that folder run `pnpm install` and `pnpm dev` after `poetry build` in this repository root (see `github-io/README.md`: local wheel is served from `dist/`, foundation still from PyPI). Dependencies use published `@cadbuildr/cad-kernel-r3f` and `@cadbuildr/cad-pyodide-runtime` on npm, not monorepo workspace links.
