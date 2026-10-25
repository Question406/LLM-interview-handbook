import { createHash } from "node:crypto";
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Shared by local dev servers for this checkout. Credentials stay in a private
// temporary file and are never returned to the browser or written to the repo.
export function connectionFile(root = process.cwd()) {
  return join(tmpdir(), `handbook-runner-${createHash("sha256").update(root).digest("hex").slice(0, 16)}.json`);
}

export function readConnection(root = process.cwd()) {
  try {
    const value = JSON.parse(readFileSync(connectionFile(root), "utf8"));
    if (typeof value.token !== "string" || !/^[a-f0-9]{64}$/.test(value.token)) return null;
    if (!Number.isInteger(value.port) || value.port < 1 || value.port > 65535) return null;
    return { token: value.token, port: value.port };
  } catch { return null; }
}

export function publishConnection(token, port, root = process.cwd()) {
  writeFileSync(connectionFile(root), JSON.stringify({ token, port: Number(port) }), { mode: 0o600 });
}

export function clearConnection(token, root = process.cwd()) {
  if (readConnection(root)?.token === token) {
    try { unlinkSync(connectionFile(root)); } catch { /* already removed */ }
  }
}
