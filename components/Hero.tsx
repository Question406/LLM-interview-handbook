"use client";

import type { Handbook, HandbookCompanyFacet } from "@/content/types";
import { qualifiedId } from "@/lib/handbook";

export function Hero({
  handbook,
  masteredCount,
  mastered,
  onOpenSection,
  onOpenCompany,
  onRandomQuestion,
}: {
  handbook: Handbook;
  masteredCount: number;
  mastered: ReadonlySet<string>;
  onOpenSection: (sectionId: string) => void;
  onOpenCompany: (companyId: string) => void;
  onRandomQuestion: () => void;
}) {
  const companies = handbook.companies ?? [];

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><span /> {handbook.shortTitle} · {handbook.edition}</div>
          <h1>{companies.length > 0 ? "为某个主题，或为哪家公司，先看什么。" : "按主题看要刷什么。"}</h1>
          <p>{handbook.description}</p>
          <div className="audience-line">{handbook.audience}</div>
          <div className="hero-actions">
            <button type="button" className="secondary-action" onClick={onRandomQuestion}>随机抽一题</button>
          </div>
        </div>
        <dl className="hero-stats" aria-label="手册数据摘要">
          <div><dt>题目</dt><dd>{handbook.stats.questions}</dd></div>
          <div><dt>S 级必会</dt><dd>{handbook.stats.mustKnow}</dd></div>
          <div><dt>模块</dt><dd>{handbook.sections.length}</dd></div>
          <div><dt>已掌握</dt><dd>{masteredCount}</dd></div>
        </dl>
      </section>

      <section className="chapter-index" id="by-topic" aria-label="主题">
        <header className="chapter-index-head">
          <h2>按主题</h2>
          <p>点进去先看这一章的导航或 S 级，再刷其余题。</p>
        </header>
        <div className="chapter-grid">
          {handbook.sections.map((section, index) => {
            const done = section.questions.filter((question) => mastered.has(qualifiedId(handbook.id, question.id))).length;
            const percent = section.questions.length ? (done / section.questions.length) * 100 : 0;
            return (
              <button type="button" className="chapter-card" key={section.id} onClick={() => onOpenSection(section.id)}>
                <span className="chapter-kicker">{String(index + 1).padStart(2, "0")}</span>
                <span className="chapter-title">{section.title.replace(/^\d+\s*·\s*/, "")}</span>
                <span className="chapter-desc">{section.description}</span>
                <span className="chapter-foot">
                  <span>{done} / {section.questions.length}</span>
                  <span className="chapter-bar"><span style={{ width: `${percent}%` }} /></span>
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {companies.length > 0 && (
        <section className="chapter-index" id="by-company" aria-label="公司">
          <header className="chapter-index-head">
            <h2>按公司</h2>
            <p>点进去先看这家要准备什么，题仍按原章节分组。</p>
          </header>
          <div className="chapter-grid">
            {companies.map((company: HandbookCompanyFacet, index) => (
              <button type="button" className="chapter-card" key={company.id} onClick={() => onOpenCompany(company.id)}>
                <span className="chapter-kicker">{String(index + 1).padStart(2, "0")}</span>
                <span className="chapter-title">{company.title}</span>
                <span className="chapter-desc">先看导航和备考地图，再按章节往下刷。</span>
                <span className="chapter-foot">
                  <span>{company.questionCount} 题</span>
                  <span className="chapter-bar"><span style={{ width: "0%" }} /></span>
                </span>
              </button>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
