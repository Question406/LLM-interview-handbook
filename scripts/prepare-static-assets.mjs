import { copyFileSync, existsSync, mkdirSync, readdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceDirectory = resolve(projectRoot, "node_modules/katex/dist/fonts");
const targetDirectory = resolve(projectRoot, "public/_next/static/css/fonts");

if (!existsSync(sourceDirectory)) throw new Error("KaTeX fonts are missing. Run npm install before building the site.");
mkdirSync(targetDirectory, { recursive: true });

const fontFiles = readdirSync(sourceDirectory).filter((file) => file.endsWith(".woff2"));
for (const fontFile of fontFiles) copyFileSync(resolve(sourceDirectory, fontFile), resolve(targetDirectory, fontFile));

console.log(`Prepared ${fontFiles.length} KaTeX webfonts.`);
