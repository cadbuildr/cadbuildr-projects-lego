"""CADbuildr Code CLI banner as a compact stud matrix (B / O) with brand colors.

Layout matches ``py/packages/cadbuildr/code/cadbuildr/code/logo.ans``:
``B`` ← ``#``, ``O`` ← ``/``, ``.`` ← empty.

Hex colors match ``tsjs/packages/atoms/brand-identity/src/components/Logo/logo_dark.svg``:
``#40494b`` (outer path) and ``#E87724`` (inner path).
"""

from __future__ import annotations

from .pixel_art import ColorMatrix

# logo_dark.svg path fills (brand identity)
CADBUILDR_CODE_LOGO_BRAND_HEX_B = "#40494b"
CADBUILDR_CODE_LOGO_BRAND_HEX_O = "#E87724"

CADBUILDR_CODE_LOGO_COMPACT = """\
..........B.....B..........
........BBBB...BBBB........
...BB..BBBBBBBBBBBBB..BB...
..BBBBBBB.........BBBBBBB..
...BBBB..O......OO..BBBB...
BBBBBB..OO......OOO..BBBBBB
BBBBBB..OOOO...OOOO..BBBBBB
...BBBB...OOOOOOO...BBB....
.BBBBBBBBB.OOOOO.BBBBBBBB..
...B....BB.OOOOO.BB....B...
........BB.OOOOO.BB........
...........OOOOO...........
...........O.O.O...........
...........O.O.O...........
...........O.O.............
...........O.O.............
...........O...............
...........O...............
"""


def matrix_from_cadbuildr_code_logo_compact(compact: str | None = None) -> ColorMatrix:
    """Expand ``B`` / ``O`` / ``.`` rows into a :class:`ColorMatrix` (``None`` for empty)."""
    text = (compact if compact is not None else CADBUILDR_CODE_LOGO_COMPACT).strip()
    out: ColorMatrix = []
    for line in text.splitlines():
        stripped = line.rstrip("\n\r")
        if not stripped:
            continue
        row: list[str | None] = []
        for ch in stripped:
            if ch == "B":
                row.append(CADBUILDR_CODE_LOGO_BRAND_HEX_B)
            elif ch == "O":
                row.append(CADBUILDR_CODE_LOGO_BRAND_HEX_O)
            elif ch in ". ":
                row.append(None)
            else:
                raise ValueError(f"Invalid compact logo character {ch!r}; expected B, O, or .")
        out.append(row)
    width = max((len(r) for r in out), default=0)
    for r in out:
        if len(r) < width:
            r.extend([None] * (width - len(r)))
    return out


CADBUILDR_CODE_LOGO_MATRIX: ColorMatrix = matrix_from_cadbuildr_code_logo_compact()
