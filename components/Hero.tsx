"use client";

import type { Handbook } from "@/content/types";
import { qualifiedId } from "@/lib/handbook";

export function Hero({
  handbook,
  masteredCount,
  mastered,
  onOpenSection,
  onRandomQuestion,
}: {
  handbook: Handbook;
  masteredCount: number;
  mastered: ReadonlySet<string>;
  onOpenSection: (sectionId: string) => void;
  onRandomQuestion: () => void;
}) {
  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><span /> {handbook.shortTitle} · {handbook.edition}</div>
          <h1>把知识点，变成你的面试反射。</h1>
          <p>{handbook.description}</p>
          <div className="audience-line">{handbook.audience}</div>
          <div className="hero-actions">
            <button type="button" className="primary-action" onClick={() => onOpenSection(handbook.sections[0].id)}>从第一章开始</button>
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

      <section className="chapter-index" aria-label="知识模块">
        <header className="chapter-index-head">
          <h2>按模块开始</h2>
          <p>先看高亮的 30 秒口播，再展开完整推导。</p>
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
    </>
  );
}
