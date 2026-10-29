import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import matter from "gray-matter";
import { formatQuestionSource } from "../lib/format-question-source.mjs";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const write = process.argv.includes("--write");
const auditIndex = process.argv.indexOf("--audit");
const auditPath = auditIndex < 0 ? null : resolve(process.argv[auditIndex + 1]);
const files = (directory) =>
  readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = join(directory, entry.name);
    if (entry.isDirectory()) return entry.name === "drafts" ? [] : files(file);
    return entry.name.endsWith(".md") ? [file] : [];
  });
const report = {
  files: 0,
  changedFiles: 0,
  blocks: 0,
  changedBlocks: 0,
  languages: {},
  changes: [],
};
const audit = [];
for (const file of files(join(root, "content/handbooks"))) {
  const source = readFileSync(file, "utf8");
  const { data } = matter(source);
  let blocks = 0;
  let changed = 0;
  let formatted;
  try {
    formatted = formatQuestionSource(source, {
      legacyHtml: data.format === "legacy-html",
      onBlock(block) {
        blocks += 1;
        report.blocks += 1;
        const language = block.language || "unlabelled";
        report.languages[language] ??= { blocks: 0, changed: 0 };
        report.languages[language].blocks += 1;
        if (block.before !== block.after) {
          changed += 1;
          report.changedBlocks += 1;
          report.languages[language].changed += 1;
        }
        if (auditPath) audit.push({ file: relative(root, file), ...block });
      },
    });
  } catch (cause) {
    throw new Error(`${relative(root, file)}: ${cause.message}`, { cause });
  }
  if (blocks) report.files += 1;
  if (formatted !== source) {
    report.changedFiles += 1;
    report.changes.push({ file: relative(root, file), changedBlocks: changed });
    if (write) writeFileSync(file, formatted);
  }
}
if (auditPath) {
  mkdirSync(dirname(auditPath), { recursive: true });
  writeFileSync(
    auditPath,
    `${JSON.stringify({ ...report, audit }, null, 2)}\n`,
  );
}
console.log(
  `${write ? "Formatted" : "Checked"} ${report.blocks} code blocks in ${report.files} files; ` +
    `${report.changedBlocks} blocks in ${report.changedFiles} files ${write ? "updated" : "need formatting"}.`,
);
console.log(JSON.stringify(report.languages));
if (!write && report.changedFiles) process.exitCode = 1;
