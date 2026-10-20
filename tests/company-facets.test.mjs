import assert from "node:assert/strict";
import test from "node:test";
import {
  loadCompanyRegistry,
  resolveQuestionCompanies,
  companyFacetsForQuestions,
} from "../lib/company-facets.mjs";

const registry = loadCompanyRegistry();

test("explicit companies win over section and tag inference", () => {
  assert.deepEqual(
    resolveQuestionCompanies({
      companies: ["alibaba"],
      sectionId: "openai",
      tags: ["OpenAI", "GRPO"],
    }, registry),
    ["alibaba"],
  );
});

test("a company-named section infers that company", () => {
  assert.deepEqual(
    resolveQuestionCompanies({ sectionId: "openai", tags: ["KV Cache"] }, registry),
    ["openai"],
  );
});

test("alibaba-oa maps to alibaba", () => {
  assert.deepEqual(
    resolveQuestionCompanies({ sectionId: "alibaba-oa", tags: ["OA"] }, registry),
    ["alibaba"],
  );
});

test("known tag aliases infer companies on a topic section", () => {
  assert.deepEqual(
    resolveQuestionCompanies({ sectionId: "posttrain", tags: ["ByteDance", "GRPO"] }, registry),
    ["bytedance"],
  );
});

test("section and tags merge when companies is omitted", () => {
  assert.deepEqual(
    resolveQuestionCompanies({ sectionId: "alibaba", tags: ["ByteDance"] }, registry),
    ["alibaba", "bytedance"],
  );
});

test("topic sections with no company tags stay untagged", () => {
  assert.deepEqual(
    resolveQuestionCompanies({ sectionId: "posttrain", tags: ["GRPO", "Advantage"] }, registry),
    [],
  );
});

test("unknown explicit company slugs fail", () => {
  assert.throws(
    () => resolveQuestionCompanies({
      companies: ["NotACo"],
      sectionId: "posttrain",
      tags: ["GRPO"],
    }, registry),
    /unknown company/i,
  );
});

test("company facets keep registry order and drop unused ids", () => {
  const facets = companyFacetsForQuestions([
    { companies: ["xai", "openai"] },
    { companies: ["openai"] },
    { companies: [] },
  ], registry);
  assert.deepEqual(facets.map((facet) => facet.id), ["openai", "xai"]);
  assert.equal(facets[0].questionCount, 2);
  assert.equal(facets[1].questionCount, 1);
  assert.equal(facets[0].title, "OpenAI");
});
