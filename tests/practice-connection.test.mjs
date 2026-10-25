import assert from "node:assert/strict";
import { mkdtempSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { connectionFile, readConnection, publishConnection, clearConnection } from "../scripts/practice-connection.mjs";

test("existing local handbook servers can discover a private runner connection", () => {
  const root = mkdtempSync(join(tmpdir(), "handbook-connection-test-"));
  const token = "a".repeat(64);
  try {
    assert.equal(readConnection(root), null);
    publishConnection(token, 8765, root);
    assert.deepEqual(readConnection(root), { token, port: 8765 });
    assert.equal(statSync(connectionFile(root)).mode & 0o777, 0o600);
    // An older launcher must not erase a newer launcher's credentials.
    publishConnection("b".repeat(64), 8766, root);
    clearConnection(token, root);
    assert.equal(readConnection(root).port, 8766);
    clearConnection("b".repeat(64), root);
    assert.equal(readConnection(root), null);
  } finally {
    clearConnection("b".repeat(64), root);
    rmSync(root, { recursive: true });
  }
});

test("malformed runner connection files cannot redirect the proxy", () => {
  const root = mkdtempSync(join(tmpdir(), "handbook-connection-test-"));
  const token = "a".repeat(64);
  try {
    publishConnection(token, 8765, root);
    writeFileSync(connectionFile(root), JSON.stringify({ token, port: "https://external.example" }));
    assert.equal(readConnection(root), null);
    writeFileSync(connectionFile(root), JSON.stringify({ token: "invalid", port: 8765 }));
    assert.equal(readConnection(root), null);
    // Restore a valid record so cleanup uses the ordinary ownership check.
    publishConnection(token, 8765, root);
  } finally {
    clearConnection(token, root);
    rmSync(root, { recursive: true });
  }
});
