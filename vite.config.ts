import { existsSync, readFileSync } from "node:fs";
import { extname, relative, resolve } from "node:path";
import { gzipSync } from "node:zlib";
import { sites } from "@openai/sites-vite-plugin";
import vinext from "vinext";
import { defineConfig } from "vite";
import hostingConfig from "./.openai/hosting.json";

function gzipContentJson() {
  const publicDir = resolve(process.cwd(), "public");
  return {
    name: "gzip-content-json",
    configureServer(server: { middlewares: { use: (handler: (req: unknown, res: unknown, next: () => void) => void) => void } }) {
      server.middlewares.use((req, res, next) => {
        const request = req as { url?: string; headers: { [key: string]: string | string[] | undefined } };
        const response = res as { setHeader: (name: string, value: string) => void; end: (body: Buffer) => void };
        const pathname = request.url?.split("?")[0] ?? "";
        if (!pathname.startsWith("/content/") || extname(pathname) !== ".json") {
          next();
          return;
        }
        if (!String(request.headers["accept-encoding"] ?? "").includes("gzip")) {
          next();
          return;
        }
        const filePath = resolve(publicDir, pathname.slice(1));
        const relativePath = relative(publicDir, filePath);
        if (relativePath.startsWith("..") || relativePath.includes("..")) {
          next();
          return;
        }
        if (!existsSync(filePath)) {
          next();
          return;
        }
        const body = gzipSync(readFileSync(filePath));
        response.setHeader("Content-Type", "application/json; charset=utf-8");
        response.setHeader("Content-Encoding", "gzip");
        response.setHeader("Vary", "Accept-Encoding");
        response.setHeader("Cache-Control", "no-cache");
        response.end(body);
      });
    },
  };
}

const SITE_CREATOR_PLACEHOLDER_DATABASE_ID =
  "00000000-0000-4000-8000-000000000000";

const { d1, r2 } = hostingConfig;

// macOS Seatbelt blocks FSEvents, so Codex previews need polling for HMR.
const isCodexSeatbeltSandbox = process.env.CODEX_SANDBOX === "seatbelt";

const localBindingConfig = {
  main: "./worker/index.ts",
  compatibility_flags: ["nodejs_compat"],
  d1_databases: d1
    ? [
        {
          binding: d1,
          database_name: "site-creator-d1",
          database_id: SITE_CREATOR_PLACEHOLDER_DATABASE_ID,
        },
      ]
    : [],
  r2_buckets: r2
    ? [
        {
          binding: r2,
          bucket_name: "site-creator-r2",
        },
      ]
    : [],
};

export default defineConfig(async () => {
  // Keep Wrangler and Miniflare state project-local. These are non-secret tool
  // settings; application environment belongs in ignored `.env*` files.
  process.env.WRANGLER_WRITE_LOGS ??= "false";
  process.env.WRANGLER_LOG_PATH ??= ".wrangler/logs";
  process.env.MINIFLARE_REGISTRY_PATH ??= ".wrangler/registry";

  // Wrangler snapshots its log path while the Cloudflare plugin is imported.
  const { cloudflare } = await import("@cloudflare/vite-plugin");

  return {
    server: {
      watch: {
        ignored: ["**/content/generated/**", "**/public/content/**", "**/.wrangler/**"],
        ...(isCodexSeatbeltSandbox ? { useFsEvents: false, usePolling: true } : {}),
      },
    },
    plugins: [
      gzipContentJson(),
      vinext(),
      sites(),
      cloudflare({
        viteEnvironment: { name: "rsc", childEnvironments: ["ssr"] },
        config: localBindingConfig,
      }),
    ],
  };
});
