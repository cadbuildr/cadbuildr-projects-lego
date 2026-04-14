# lego-github-io

GitHub Pages-style showcase app for:

- `@cadbuildr/cad-kernel-r3f`
- `@cadbuildr/cad-pyodide-runtime`
- your open-source LEGO python package

The app runs Python in-browser (Pyodide + Foundation), executes LEGO examples,
posts the DAG to `kernel-api`, and renders STL meshes in R3F.

## What is in this demo

- Example gallery with richer LEGO scenes (`LegoFort`, `MatrixLegoArt`, custom skyline).
- Drag-and-drop image/logo converter that maps image colors to LEGO palette and generates
  `MatrixLegoArt` dynamically.
- Code panel showing the generated Python that can be reused in docs/examples.

## Run locally

`index.html` loads Pyodide from jsDelivr (`v0.29.3`, matching `@cadbuildr/cad-pyodide-runtime`) so `initializeCadPyodideRuntime` finds `globalThis.loadPyodide`. The `pyodide` npm package is listed as a dependency to satisfy the runtime’s peer dependency; you can instead pass `loadPyodide` from `import { loadPyodide } from "pyodide"` if you bundle Pyodide yourself.

From this directory (`github-io/`):

```bash
pnpm install
pnpm dev
```

Defaults:

- Kernel API: `@cadbuildr/cad-kernel-r3f` calls the hosted `https://kernel-api.cadbuildr.com` (CORS must allow your site origin).
- Foundation: `cadbuildr.foundation` / **`cadbuildr-foundation`** on **PyPI** (micropip).
- LEGO: **`cadbuildr_projects.lego`** from a **wheel built in this repo**, not from PyPI.

**Local LEGO wheel (this repository)**

1. Build the Python package wheel once (or after Python changes) from the repo root (parent of `github-io/`):

   ```bash
   cd ..
   poetry build
   ```

2. **Dev:** Vite serves that file from `../dist/…whl` at `/local-lego/cadbuildr_projects_lego-0.1.0-py3-none-any.whl` (see `src/legoLocal.ts` if the version changes).

3. **Static / GitHub Pages build:** copy the wheel into the app’s public folder, then build:

   ```bash
   pnpm run sync-lego-wheel
   pnpm run build
   ```

   (`sync-lego-wheel` runs `poetry build` in the lego package and copies `../dist/*.whl` into `public/local-lego/`, which Vite emits as `local-lego/*.whl`.)

### Optional: override wheel URL

```bash
VITE_LEGO_PACKAGE_WHEEL_URL=https://example.com/path/cadbuildr_projects_lego-0.1.0-py3-none-any.whl
```

## Build static assets for GitHub Pages

```bash
pnpm run build
```

Output: `github-io/dist` — upload that folder as the Pages artifact (or use an Action that runs `vite build` and publishes `dist`).

**Not quite “push and forget” until you configure the following at build time:**

| Concern | What you need |
|--------|----------------|
| Asset base URL | For project sites (`username.github.io/repo/`), set `VITE_APP_BASE_PATH=/repo-name/` (trailing slash). User/organization root site can keep `/`. |
| LEGO wheel | Ship `public/local-lego/*.whl` (use `sync-lego-wheel`) or set `VITE_LEGO_PACKAGE_WHEEL_URL` to an absolute URL. Foundation still loads from PyPI via micropip. |
| npm deps | This repo’s `package.json` uses published `@cadbuildr/cad-kernel-r3f` and `@cadbuildr/cad-pyodide-runtime` (no pnpm workspace protocol). Pin versions as needed in CI. |

After that, the built site is static and suitable for GitHub Pages.
