import type { IncomingMessage, ServerResponse } from "node:http";
import { request as httpRequest } from "node:http";
import type { Plugin } from "vite";
import { readConnection } from "./practice-connection.mjs";

/** Dev-only proxy. The bearer token is server-side and never sent to the browser. */
export function localPracticeProxy(): Plugin {
  return {
    name: "local-python-practice",
    configureServer(server) {
      server.middlewares.use((req: IncomingMessage, res: ServerResponse, next) => {
        if (!req.url?.startsWith("/api/practice/")) return next();
        const reject = (status: number, error: string) => {
          res.writeHead(status, { "Content-Type": "application/json", "Cache-Control": "no-store" });
          res.end(JSON.stringify({ error }));
        };
        const connection = readConnection();
        const token = process.env.PRACTICE_RUNNER_TOKEN ?? connection?.token;
        const port = process.env.PRACTICE_RUNNER_PORT ?? connection?.port ?? "8765";
        if (!token) return reject(503, "请用 npm run practice 启动本地编程环境。");
        const host = req.headers.host ?? "";
        if (!/^(localhost|127\.0\.0\.1):\d+$/.test(host)) return reject(403, "Localhost only");
        const origin = req.headers.origin;
        if (origin && origin !== `http://${host}`) return reject(403, "Same-origin requests only");
        if (req.method === "POST" && !req.headers["content-type"]?.startsWith("application/json")) return reject(415, "JSON required");
        const path = req.url.slice("/api/practice".length);
        if (!/^\/(health|exercise|run|stop)(\?|$)/.test(path)) return reject(404, "Not found");
        const upstream = httpRequest({ hostname: "127.0.0.1", port, path, method: req.method,
          headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json",
            ...(req.headers["content-length"] ? { "Content-Length": req.headers["content-length"] } : {}) },
        }, (response) => {
          res.writeHead(response.statusCode ?? 502, { "Content-Type": "application/json", "Cache-Control": "no-store" });
          response.pipe(res);
        });
        upstream.on("error", () => { if (!res.headersSent) reject(503, "Python 运行器未连接，请重新启动 npm run practice。"); });
        req.pipe(upstream);
      });
    },
  };
}
