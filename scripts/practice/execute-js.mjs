import assert from "node:assert/strict";
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { join } from "node:path";

const request = JSON.parse(readFileSync(process.argv[2], "utf8"));
const target = join(process.cwd(), "solution.mjs");
const offset = request.code.split("\n").length + 2;
const checks = [];
const result = { status: "passed", error: null, checks, plots: [] };
function location(stack) {
  const match = String(stack).match(/solution\.mjs:(\d+):(\d+)/);
  const line = match ? Number(match[1]) : null;
  return { file: line && line > offset ? "test_code.py" : "user_code.py", line: line && line > offset ? line - offset : line };
}
for (const method of ["equal", "deepEqual", "strictEqual", "deepStrictEqual", "ok", "throws", "rejects", "notEqual"]) {
  const original = assert[method];
  assert[method] = (...args) => {
    const position = location(new Error().stack);
    const record = (passed) => { if (position.file === "test_code.py") checks.push({ line: position.line, label: `assert.${method}(…)`, passed }); };
    try {
      const value = original(...args);
      if (value?.then) return value.then((resolved) => { record(true); return resolved; }, (error) => { record(false); throw error; });
      record(true); return value;
    } catch (error) { record(false); throw error; }
  };
}
writeFileSync(target, `${request.code}\n\n// Default tests\n${request.tests ?? ""}`);
try {
  await import(pathToFileURL(target).href);
} catch (error) {
  result.status = "failed";
  result.error = { type: error.name, message: error.message, ...location(error.stack), traceback: error.stack };
}
writeFileSync(process.argv[3], JSON.stringify(result));
