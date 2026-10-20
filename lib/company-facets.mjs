import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const registryPath = resolve(dirname(fileURLToPath(import.meta.url)), "../content/companies.json");

/** @typedef {{ id: string, title: string, aliases: string[], sections: string[] }} CompanyRecord */
/** @typedef {{ byId: Map<string, CompanyRecord>, byAlias: Map<string, string>, bySection: Map<string, string>, list: CompanyRecord[] }} CompanyRegistry */

function fail(message) {
  throw new Error(message);
}

export function loadCompanyRegistry(filePath = registryPath) {
  const parsed = JSON.parse(readFileSync(filePath, "utf8"));
  if (!parsed || !Array.isArray(parsed.companies) || !parsed.companies.length) {
    fail("content/companies.json must list companies");
  }

  /** @type {CompanyRecord[]} */
  const list = [];
  const byId = new Map();
  const byAlias = new Map();
  const bySection = new Map();

  for (const raw of parsed.companies) {
    if (!raw || typeof raw !== "object") fail("each company must be an object");
    const id = typeof raw.id === "string" ? raw.id.trim() : "";
    if (!/^[a-z0-9][a-z0-9-]*$/.test(id)) fail(`company id ${id || "(empty)"} must be a kebab-case slug`);
    if (byId.has(id)) fail(`duplicate company id ${id}`);
    const title = typeof raw.title === "string" ? raw.title.trim() : "";
    if (!title) fail(`company ${id} needs a title`);
    const aliases = Array.isArray(raw.aliases) ? raw.aliases.map((alias) => String(alias).trim()).filter(Boolean) : [];
    const sections = Array.isArray(raw.sections) ? raw.sections.map((section) => String(section).trim()).filter(Boolean) : [];
    const record = { id, title, aliases, sections };
    byId.set(id, record);
    list.push(record);
    for (const alias of [id, title, ...aliases]) {
      const key = alias.toLocaleLowerCase();
      const existing = byAlias.get(key);
      if (existing && existing !== id) fail(`company alias ${alias} maps to both ${existing} and ${id}`);
      byAlias.set(key, id);
    }
    for (const section of sections) {
      const existing = bySection.get(section);
      if (existing && existing !== id) fail(`section ${section} maps to both ${existing} and ${id}`);
      bySection.set(section, id);
    }
  }

  return { byId, byAlias, bySection, list };
}

function uniqueSlugs(values) {
  const seen = new Set();
  const slugs = [];
  for (const value of values) {
    if (!value || seen.has(value)) continue;
    seen.add(value);
    slugs.push(value);
  }
  return slugs;
}

/**
 * @param {{ companies?: string[], sectionId: string, tags: string[] }} question
 * @param {CompanyRegistry} registry
 */
export function resolveQuestionCompanies(question, registry) {
  if (Array.isArray(question.companies)) {
    if (question.companies.some((value) => typeof value !== "string" || !value.trim())) {
      fail("companies must be a list of slugs");
    }
    const slugs = uniqueSlugs(question.companies.map((value) => value.trim()));
    for (const slug of slugs) {
      if (!registry.byId.has(slug)) fail(`unknown company ${slug}`);
    }
    return slugs;
  }

  const inferred = [];
  const fromSection = registry.bySection.get(question.sectionId);
  if (fromSection) inferred.push(fromSection);
  for (const tag of question.tags ?? []) {
    const slug = registry.byAlias.get(String(tag).trim().toLocaleLowerCase());
    if (slug) inferred.push(slug);
  }
  return uniqueSlugs(inferred);
}

/**
 * @param {{ companies: string[] }[]} questions
 * @param {CompanyRegistry} registry
 */
export function companyFacetsForQuestions(questions, registry) {
  const counts = new Map();
  for (const question of questions) {
    for (const slug of new Set(question.companies ?? [])) {
      counts.set(slug, (counts.get(slug) ?? 0) + 1);
    }
  }
  return registry.list
    .filter((company) => counts.has(company.id))
    .map((company) => ({
      id: company.id,
      title: company.title,
      questionCount: counts.get(company.id),
    }));
}

export function questionMatchesCompany(question, companyId) {
  if (!companyId) return true;
  return Array.isArray(question.companies) && question.companies.includes(companyId);
}

export function handbookHasCompanies(handbook) {
  if (Array.isArray(handbook?.companies) && handbook.companies.length > 0) return true;
  return (handbook?.sections ?? []).some((section) => (
    (section.questions ?? []).some((question) => Array.isArray(question.companies) && question.companies.length > 0)
  ));
}
