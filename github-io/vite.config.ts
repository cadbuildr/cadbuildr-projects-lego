import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig, type Plugin } from "vite";

import { LOCAL_LEGO_URL_SEGMENT, LOCAL_LEGO_WHEEL_FILE } from "./src/legoLocal";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** Dev-only: stream the wheel from `../dist/` (run `poetry build` in the lego package dir). */
function serveLocalLegoWheelFromDist(): Plugin {
  return {
    name: "serve-local-lego-wheel-from-dist",
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const pathname = req.url?.split("?")[0] ?? "";
        const tail = `/${LOCAL_LEGO_URL_SEGMENT}/${LOCAL_LEGO_WHEEL_FILE}`;
        if (!pathname.endsWith(tail)) {
          next();
          return;
        }
        const wheelPath = path.resolve(__dirname, "..", "dist", LOCAL_LEGO_WHEEL_FILE);
        if (!fs.existsSync(wheelPath)) {
          res.statusCode = 404;
          res.setHeader("Content-Type", "text/plain; charset=utf-8");
          res.end(
            `Missing LEGO wheel at ${wheelPath}.\nRun: cd py/packages/cadbuildr_projects/lego && poetry build`
          );
          return;
        }
        res.setHeader("Content-Type", "application/octet-stream");
        fs.createReadStream(wheelPath).pipe(res);
      });
    },
  };
}

export default defineConfig({
  base: (process.env.VITE_APP_BASE_PATH as string | undefined) ?? "/",
  plugins: [react(), serveLocalLegoWheelFromDist()],
  server: {
    host: "0.0.0.0",
    port: 3007,
    // Optional: same-origin `/v1` → local kernel-api for ad-hoc testing (the demo uses the hosted API from `@cadbuildr/cad-kernel-r3f`).
    proxy: {
      "/v1": { target: "http://127.0.0.1:8087", changeOrigin: true },
    },
  },
  build: {
    outDir: "dist",
  },
});
