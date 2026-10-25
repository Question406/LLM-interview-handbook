import { spawn, spawnSync } from "node:child_process";
import { randomBytes } from "node:crypto";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { publishConnection, clearConnection } from "./practice-connection.mjs";

const root = process.cwd();
const probe = spawnSync("python3", ["-c", "import sys;sys.path.insert(0,'scripts/practice');from setup import python_path;print(python_path())"], { encoding: "utf8" });
if (probe.status !== 0) throw new Error(probe.stderr || "Python 3.11+ required");
const python = probe.stdout.trim();
if (!existsSync(python)) {
  console.error("请先运行 npm run practice:setup 安装 Python 依赖。");
  process.exit(1);
}
if (!existsSync("public/content/catalog.json")) {
  const build = spawnSync("npm", ["run", "content:build"], { stdio: "inherit" });
  if (build.status !== 0) process.exit(build.status ?? 1);
}
const assets = spawnSync("npm", ["run", "assets:build"], { stdio: "inherit" });
if (assets.status !== 0) process.exit(assets.status ?? 1);
const environment = { ...process.env, PRACTICE_RUNNER_TOKEN: randomBytes(32).toString("hex"),
  PRACTICE_RUNNER_PORT: process.env.PRACTICE_RUNNER_PORT ?? "8765", WRANGLER_LOG_PATH: ".wrangler/wrangler.log",
  VINEXT_NO_DEV_LOCK: "1" };
const children = [];
let closing = false;
function close(code = 0) {
  if (closing) return;
  closing = true;
  clearConnection(environment.PRACTICE_RUNNER_TOKEN);
  for (const child of children) child.kill("SIGTERM");
  process.exitCode = code;
}
for (const event of ["SIGINT", "SIGTERM"]) process.on(event, () => close());
function launch(command, args) {
  const child = spawn(command, args, { cwd: root, env: environment, stdio: "inherit" });
  children.push(child);
  child.on("error", (error) => { console.error(error.message); close(1); });
  child.on("exit", (code) => close(code ?? 1));
  return child;
}
launch(python, ["-u", "scripts/practice/server.py"]);
// Publish only after the new runner has authenticated successfully. This also
// lets an already-running ordinary handbook server use the same local runner.
let ready = false;
for (let attempt = 0; attempt < 50 && !closing; attempt++) {
  try {
    const response = await fetch(`http://127.0.0.1:${environment.PRACTICE_RUNNER_PORT}/health`, {
      headers: { Authorization: `Bearer ${environment.PRACTICE_RUNNER_TOKEN}` }, signal: AbortSignal.timeout(500),
    });
    if (response.ok) { ready = true; break; }
  } catch { /* runner still starting */ }
  await new Promise((resolve) => setTimeout(resolve, 100));
}
if (!ready || closing) {
  console.error("本地 Python 运行器未能启动，请检查端口或上方报错。");
  close(1);
} else {
publishConnection(environment.PRACTICE_RUNNER_TOKEN, environment.PRACTICE_RUNNER_PORT);
// A separate port keeps any existing handbook dev session untouched.
const port = process.env.PRACTICE_PORT ?? "3001";
launch(process.execPath, [resolve("node_modules/vinext/dist/cli.js"), "dev", "--hostname", "127.0.0.1", "--port", port]);
console.log(`\n编程练习：http://127.0.0.1:${port}/practice\n`);
}
