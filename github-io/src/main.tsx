import React from "react";
import ReactDOM from "react-dom/client";
import { OrbitControls } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import { KernelApiClient, KernelStlMesh, type KernelDag } from "@cadbuildr/cad-kernel-r3f";
import {
  initializeCadPyodideRuntime,
  runCadPythonCode,
  type PyodideLike,
} from "@cadbuildr/cad-pyodide-runtime";

import { ColoredKernelMeshGroup } from "./ColoredKernelMeshGroup";
import { LOCAL_LEGO_URL_SEGMENT, LOCAL_LEGO_WHEEL_FILE } from "./legoLocal";
import "./styles.css";

type DemoExample = {
  id: string;
  title: string;
  description: string;
  color: string;
  buildPythonCode: () => string;
};

type LogoPixelArtState = {
  matrix: string[][];
  width: number;
  height: number;
  sourceName: string;
};

const FOUNDATION_IMPORT_PATH =
  (import.meta.env.VITE_FOUNDATION_IMPORT_PATH as string | undefined) ?? "cadbuildr.foundation";
const FOUNDATION_PACKAGE_NAME =
  (import.meta.env.VITE_FOUNDATION_PACKAGE_NAME as string | undefined) ?? "cadbuildr-foundation";
const FOUNDATION_VERSION =
  (import.meta.env.VITE_FOUNDATION_VERSION as string | undefined) ?? "^0.2.0";
const FOUNDATION_DAG_UTILS_PATH = `${FOUNDATION_IMPORT_PATH}.dag_utils`;

const LEGO_IMPORT_PATH =
  (import.meta.env.VITE_LEGO_IMPORT_PATH as string | undefined) ?? "cadbuildr_projects.lego";
const LEGO_PACKAGE_REQUIREMENT =
  (import.meta.env.VITE_LEGO_PACKAGE_REQUIREMENT as string | undefined) ?? "";

function resolveLegoWheelUrl(): string {
  const fromEnv = (import.meta.env.VITE_LEGO_PACKAGE_WHEEL_URL as string | undefined)?.trim();
  if (fromEnv) {
    return fromEnv;
  }
  if (typeof window === "undefined") {
    return "";
  }
  return new URL(
    `${LOCAL_LEGO_URL_SEGMENT}/${LOCAL_LEGO_WHEEL_FILE}`,
    window.location.origin + import.meta.env.BASE_URL
  ).href;
}

const DEFAULT_LOGO_BLOCK_SIZE_STUDS = 2;
const MAX_LOGO_WIDTH = 24;
const MAX_LOGO_HEIGHT = 24;
const MAX_DROP_FILE_SIZE_BYTES = 8 * 1024 * 1024;

/** Foundation / kernel STLs are Z-up; R3F is Y-up — lay the plate on XZ with studs toward +Y. */
const MESH_SCENE_POSITION: [number, number, number] = [100, 0, 100];
const CAD_Z_UP_TO_Y_UP: [number, number, number] = [-Math.PI / 2, 0, 0];

function toPythonLiteral(value: unknown): string {
  if (value === null) {
    return "None";
  }
  if (typeof value === "string") {
    return JSON.stringify(value);
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => toPythonLiteral(item)).join(", ")}]`;
  }
  throw new Error(`Unsupported python literal value: ${typeof value}`);
}

function buildLogoPixelArtPythonCode(data: LogoPixelArtState, blockSizeStuds: number): string {
  return `
from ${FOUNDATION_IMPORT_PATH} import show
from ${LEGO_IMPORT_PATH} import MatrixLegoArt

matrix = ${toPythonLiteral(data.matrix)}

show(
    MatrixLegoArt(
        matrix=matrix,
        block_size_studs=${blockSizeStuds},
    )
)
`.trim();
}

const EXAMPLES: DemoExample[] = [
  {
    id: "fort",
    title: "Fortress perimeter",
    description: "LegoFort: four identical bonded walls, shared corners, centered footprint.",
    color: "#f97316",
    buildPythonCode: () => `
from ${FOUNDATION_IMPORT_PATH} import show
from ${LEGO_IMPORT_PATH} import LegoFort

show(LegoFort(n_length_studs=24, n_width_studs=24, n_layers=4))
`.trim(),
  },
  {
    id: "pixel-art",
    title: "Matrix art plate",
    description:
      "MatrixLegoArt: CADbuildr Code banner from Python (compact B/O matrix, brand hex from logo_dark.svg).",
    color: "#E87724",
    buildPythonCode: () => `
from ${FOUNDATION_IMPORT_PATH} import show
from ${LEGO_IMPORT_PATH} import CADBUILDR_CODE_LOGO_MATRIX, MatrixLegoArt

show(MatrixLegoArt(matrix=CADBUILDR_CODE_LOGO_MATRIX, block_size_studs=2))
`.trim(),
  },
  {
    id: "skyline",
    title: "Layered skyline",
    description: "A custom scene built with LegoBrick + LegoInterface grid placement helpers.",
    color: "#34d399",
    buildPythonCode: () => `
from ${FOUNDATION_IMPORT_PATH} import Assembly, show
from ${LEGO_IMPORT_PATH} import LegoBrick, LegoInterface

class LegoSkyline(Assembly):
    def __init__(self):
        super().__init__()
        interface = LegoInterface()
        palette = ["bright_red", "bright_orange", "bright_yellow", "bright_green", "bright_blue"]

        for tower_idx in range(7):
            height = 2 + (tower_idx % 4) + (tower_idx // 2)
            x_studs = tower_idx * 4
            for z_layer in range(height):
                color = palette[(tower_idx + z_layer) % len(palette)]
                interface.place(
                    LegoBrick(n_length=4, n_width=2, color=color),
                    n_x=x_studs,
                    n_y=(z_layer % 2) * 2,
                    n_z=z_layer,
                )

        for x_studs in range(0, 28, 2):
            interface.place(
                LegoBrick(n_length=2, n_width=2, short_height=True, color="dark_bluish_gray"),
                n_x=x_studs,
                n_y=-4,
                n_z=0,
            )

        interface.apply(self)

show(LegoSkyline())
`.trim(),
  },
];

function buildFoundationCompatibilityScript(foundationImportPath: string): string {
  return `
from importlib import import_module
import sys
import types

foundation = import_module(${JSON.stringify(foundationImportPath)})
_submodules = ("gen", "gen.models", "gen.runtime", "dag_utils", "utils", "helpers", "constants")
for _prefix in ("cad_package", "cadbuildr"):
    legacy_alias = _prefix + ".foundation"
    sys.modules[legacy_alias] = foundation
    _root = sys.modules.get(_prefix)
    if _root is None:
        _root = types.ModuleType(_prefix)
        _root.__path__ = []
        sys.modules[_prefix] = _root
    setattr(_root, "foundation", foundation)
    for _suffix in _submodules:
        try:
            _mod = import_module(${JSON.stringify(foundationImportPath)} + "." + _suffix)
        except ModuleNotFoundError:
            continue
        sys.modules[legacy_alias + "." + _suffix] = _mod
`.trim();
}

/** Pyodide runtime patches `builtins.show`; rebind foundation exports so `from … import show` still captures the DAG. */
function buildFoundationShowRebindScript(foundationImportPath: string): string {
  return `
import builtins
from importlib import import_module

_root = import_module(${JSON.stringify(foundationImportPath)})
_dag_utils = import_module(${JSON.stringify(foundationImportPath)} + ".dag_utils")
_hook = builtins.show
_root.show = _hook
_dag_utils.show = _hook
`.trim();
}

function buildLegoInstallScript(args: {
  packageRequirement: string;
  wheelUrl?: string;
  importPath: string;
}): string {
  return `
import importlib
import micropip

wheel_url = ${JSON.stringify(args.wheelUrl ?? "")}
package_requirement = ${JSON.stringify(args.packageRequirement)}
import_path = ${JSON.stringify(args.importPath)}
install_errors = []

try:
    importlib.import_module(import_path)
    _needs_install = False
except Exception:
    _needs_install = True

if _needs_install and wheel_url:
    try:
        await micropip.install(wheel_url, deps=False)
    except Exception as error:
        install_errors.append(f"wheel install failed: {error}")

if _needs_install and package_requirement:
    try:
        await micropip.install(package_requirement, deps=False)
    except Exception as error:
        install_errors.append(f"package install failed: {error}")

try:
    importlib.import_module(import_path)
except Exception as error:
    message = "\\n".join(install_errors) if install_errors else "No install attempt was made."
    raise RuntimeError(
        "Failed to import LEGO package '" + import_path + "'. "
        + message
        + "\\nLocal dev: run poetry build in py/packages/cadbuildr_projects/lego. "
        + "Production: copy the wheel to public/local-lego/ or set VITE_LEGO_PACKAGE_WHEEL_URL."
    ) from error
`.trim();
}

function clamp(value: number, minValue: number, maxValue: number): number {
  return Math.min(maxValue, Math.max(minValue, value));
}

function nearestPaletteColor(r: number, g: number, b: number): string {
  const palette = [
    { name: "bright_red", rgb: [201, 26, 9] as const },
    { name: "bright_orange", rgb: [231, 99, 24] as const },
    { name: "bright_yellow", rgb: [242, 205, 55] as const },
    { name: "bright_green", rgb: [75, 159, 74] as const },
    { name: "bright_blue", rgb: [0, 85, 191] as const },
    { name: "medium_azure", rgb: [54, 174, 191] as const },
    { name: "lavender", rgb: [160, 110, 185] as const },
    { name: "coral", rgb: [255, 109, 119] as const },
    { name: "white", rgb: [244, 244, 244] as const },
    { name: "black", rgb: [17, 17, 17] as const },
    { name: "tan", rgb: [222, 198, 156] as const },
    { name: "light_bluish_gray", rgb: [160, 165, 169] as const },
    { name: "dark_bluish_gray", rgb: [108, 110, 104] as const },
    { name: "reddish_brown", rgb: [88, 42, 18] as const },
  ];

  let best = palette[0];
  let bestDistance = Number.POSITIVE_INFINITY;

  for (const candidate of palette) {
    const [cr, cg, cb] = candidate.rgb;
    const distance = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2;
    if (distance < bestDistance) {
      bestDistance = distance;
      best = candidate;
    }
  }

  return best.name;
}

async function loadDroppedLogo(file: File): Promise<LogoPixelArtState> {
  if (!file.type.startsWith("image/")) {
    throw new Error("Dropped file is not an image.");
  }
  if (file.size > MAX_DROP_FILE_SIZE_BYTES) {
    throw new Error("Image is too large. Please keep it under 8MB.");
  }

  const objectUrl = URL.createObjectURL(file);
  try {
    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error("Unable to decode image."));
      image.src = objectUrl;
    });

    const maxDimension = Math.max(img.width, img.height);
    const scale = maxDimension > 0 ? Math.min(1, MAX_LOGO_WIDTH / maxDimension, MAX_LOGO_HEIGHT / maxDimension) : 1;
    const targetWidth = clamp(Math.round(img.width * scale), 1, MAX_LOGO_WIDTH);
    const targetHeight = clamp(Math.round(img.height * scale), 1, MAX_LOGO_HEIGHT);

    const canvas = document.createElement("canvas");
    canvas.width = targetWidth;
    canvas.height = targetHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      throw new Error("Could not create canvas context.");
    }

    ctx.clearRect(0, 0, targetWidth, targetHeight);
    ctx.drawImage(img, 0, 0, targetWidth, targetHeight);
    const imageData = ctx.getImageData(0, 0, targetWidth, targetHeight).data;

    const matrix: string[][] = [];
    for (let y = 0; y < targetHeight; y += 1) {
      const row: string[] = [];
      for (let x = 0; x < targetWidth; x += 1) {
        const idx = (y * targetWidth + x) * 4;
        const alpha = imageData[idx + 3];
        if (alpha < 40) {
          row.push("white");
          continue;
        }
        row.push(nearestPaletteColor(imageData[idx], imageData[idx + 1], imageData[idx + 2]));
      }
      matrix.push(row);
    }

    return {
      matrix,
      width: targetWidth,
      height: targetHeight,
      sourceName: file.name,
    };
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

function App() {
  const [activeExampleId, setActiveExampleId] = React.useState<string>(EXAMPLES[0].id);
  const [dag, setDag] = React.useState<KernelDag | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [runtimeReady, setRuntimeReady] = React.useState(false);
  const [logoPixelArt, setLogoPixelArt] = React.useState<LogoPixelArtState | null>(null);
  const [isDropTargetActive, setIsDropTargetActive] = React.useState(false);
  const [logoDropError, setLogoDropError] = React.useState<string | null>(null);
  const [logoStudSize, setLogoStudSize] = React.useState<number>(DEFAULT_LOGO_BLOCK_SIZE_STUDS);

  const pyodideRef = React.useRef<PyodideLike | null>(null);
  const runCounterRef = React.useRef(0);

  const activeExample = React.useMemo(
    () => EXAMPLES.find((example) => example.id === activeExampleId) ?? EXAMPLES[0],
    [activeExampleId]
  );

  const pythonScript = React.useMemo(() => {
    if (logoPixelArt) {
      return buildLogoPixelArtPythonCode(logoPixelArt, logoStudSize);
    }
    return activeExample.buildPythonCode();
  }, [activeExample, logoPixelArt, logoStudSize]);

  const client = React.useMemo(() => new KernelApiClient({ defaultKernel: "replicad" }), []);

  const useColoredKernelMesh = logoPixelArt !== null || activeExampleId === "pixel-art";

  React.useEffect(() => {
    let cancelled = false;

    async function bootstrapRuntime() {
      try {
        setError(null);

        const pyodide = await initializeCadPyodideRuntime({
          packages: {
            foundation: FOUNDATION_VERSION,
            foundationPackageName: FOUNDATION_PACKAGE_NAME,
          },
          foundationImportPath: FOUNDATION_IMPORT_PATH,
          foundationDagUtilsPath: FOUNDATION_DAG_UTILS_PATH,
        });
        if (cancelled) {
          return;
        }

        await pyodide.runPythonAsync(buildFoundationCompatibilityScript(FOUNDATION_IMPORT_PATH));
        await pyodide.runPythonAsync(buildFoundationShowRebindScript(FOUNDATION_IMPORT_PATH));
        await pyodide.runPythonAsync(
          buildLegoInstallScript({
            packageRequirement: LEGO_PACKAGE_REQUIREMENT,
            wheelUrl: resolveLegoWheelUrl(),
            importPath: LEGO_IMPORT_PATH,
          })
        );
        if (cancelled) {
          return;
        }

        pyodideRef.current = pyodide;
        setRuntimeReady(true);
      } catch (runtimeError) {
        if (cancelled) {
          return;
        }
        const message = runtimeError instanceof Error ? runtimeError.message : String(runtimeError);
        setError(message);
      }
    }

    void bootstrapRuntime();
    return () => {
      cancelled = true;
    };
  }, []);

  React.useEffect(() => {
    if (!runtimeReady || !pyodideRef.current) {
      return;
    }

    const runId = ++runCounterRef.current;
    let cancelled = false;

    async function runExample() {
      try {
        setError(null);
        setDag(null);

        const result = await runCadPythonCode(pyodideRef.current as PyodideLike, pythonScript, {
          foundationImportPath: FOUNDATION_IMPORT_PATH,
          foundationDagUtilsPath: FOUNDATION_DAG_UTILS_PATH,
        });

        if (cancelled || runId !== runCounterRef.current) {
          return;
        }

        setDag((result.dag as KernelDag | null) ?? null);
      } catch (runError) {
        if (cancelled || runId !== runCounterRef.current) {
          return;
        }
        const message = runError instanceof Error ? runError.message : String(runError);
        setError(message);
      }
    }

    void runExample();

    return () => {
      cancelled = true;
    };
  }, [activeExample.title, logoPixelArt, pythonScript, runtimeReady]);

  const handleDroppedFiles = React.useCallback(async (files: FileList | null) => {
    const file = files?.[0];
    if (!file) {
      return;
    }
    setLogoDropError(null);
    try {
      const generated = await loadDroppedLogo(file);
      setLogoPixelArt(generated);
      setActiveExampleId("pixel-art");
    } catch (dropError) {
      const message = dropError instanceof Error ? dropError.message : String(dropError);
      setLogoDropError(message);
    }
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <header className="sidebar-header">
          <h1>LEGO GitHub Pages Demo</h1>
        </header>

        <section className="logo-drop-card">
          <h2>Logo to LEGO pixel art</h2>
          <label
            className={`drop-zone ${isDropTargetActive ? "active" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              event.dataTransfer.dropEffect = "copy";
              setIsDropTargetActive(true);
            }}
            onDragLeave={() => setIsDropTargetActive(false)}
            onDrop={(event) => {
              event.preventDefault();
              setIsDropTargetActive(false);
              void handleDroppedFiles(event.dataTransfer.files);
            }}
          >
            <input
              type="file"
              accept="image/*"
              onChange={(event) => {
                void handleDroppedFiles(event.currentTarget.files);
                event.currentTarget.value = "";
              }}
            />
            <span>Drag and drop a logo image here</span>
            <small>or click to upload (auto-reduced to max {MAX_LOGO_WIDTH}x{MAX_LOGO_HEIGHT} studs)</small>
          </label>
          <div className="logo-controls">
            <label>
              Block size (studs)
              <input
                type="range"
                min={1}
                max={4}
                step={1}
                value={logoStudSize}
                onChange={(event) => setLogoStudSize(Number(event.currentTarget.value))}
              />
              <span>{logoStudSize}</span>
            </label>
          </div>
          {logoPixelArt ? (
            <div className="logo-summary">
              <strong>{logoPixelArt.sourceName}</strong>
              <span>
                {logoPixelArt.width} x {logoPixelArt.height} studs
              </span>
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setLogoPixelArt(null);
                  setLogoDropError(null);
                }}
              >
                Revert to preset examples
              </button>
            </div>
          ) : null}
          {logoDropError ? <p className="drop-error">{logoDropError}</p> : null}
        </section>

        <section className="example-list">
          {EXAMPLES.map((example) => (
            <button
              key={example.id}
              type="button"
              className={`example-button ${example.id === activeExample.id ? "active" : ""}`}
              onClick={() => {
                setActiveExampleId(example.id);
                setLogoPixelArt(null);
              }}
            >
              <span className="example-title">{example.title}</span>
              <span className="example-description">{example.description}</span>
            </button>
          ))}
        </section>
      </aside>

      <main className="canvas-panel">
        {error ? (
          <div className="canvas-overlay-error" role="alert">
            <pre>{error}</pre>
          </div>
        ) : null}
        <Canvas camera={{ position: [220, 140, 220], fov: 42 }}>
          <color attach="background" args={["#0b1220"]} />
          <ambientLight intensity={0.85} />
          <hemisphereLight intensity={0.3} groundColor="#1f2937" />
          <directionalLight intensity={1.1} position={[20, 40, 25]} />
          <gridHelper args={[320, 32, "#334155", "#1f2937"]} position={MESH_SCENE_POSITION} />
          <axesHelper args={[25]} position={MESH_SCENE_POSITION} />
          {dag && useColoredKernelMesh ? (
            <ColoredKernelMeshGroup
              dag={dag}
              position={MESH_SCENE_POSITION}
              rotation={CAD_Z_UP_TO_Y_UP}
              onLoaded={() => {
                setError(null);
              }}
              onError={(meshError) => {
                setError(meshError.message);
              }}
            />
          ) : null}
          {dag && !useColoredKernelMesh ? (
            <KernelStlMesh
              dag={dag}
              client={client}
              color={activeExample.color}
              meshProps={{
                position: MESH_SCENE_POSITION,
                rotation: CAD_Z_UP_TO_Y_UP,
              }}
              onError={(meshError) => {
                setError(meshError.message);
              }}
            />
          ) : null}
          <OrbitControls makeDefault target={MESH_SCENE_POSITION} />
        </Canvas>
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
