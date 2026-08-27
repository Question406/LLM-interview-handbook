"use client";

import { memo } from "react";
import type { HandbookQuestion, QuestionCardHtml } from "@/content/types";
import { displayPlain } from "@/lib/handbook";

export type CopiedKind = "link" | "prompt";

function QuestionCardView({
  question,
  index,
  isOpen,
  isMastered,
  copiedKind,
  isKeyboardActive,
  card,
  answer,
  onToggleOpen,
  onToggleMastered,
  onCopyPrompt,
  onCopyLink,
  onOpenQuestion,
  onFocus,
}: {
  question: HandbookQuestion;
  index: number;
  isOpen: boolean;
  isMastered: boolean;
  copiedKind: CopiedKind | null;
  isKeyboardActive: boolean;
  card?: QuestionCardHtml;
  answer?: string;
  onToggleOpen: () => void;
  onToggleMastered: () => void;
  onCopyPrompt: () => void;
  onCopyLink: () => void;
  onOpenQuestion: (questionId: string, book?: string | null) => void;
  onFocus: () => void;
}) {
  return (
    <article className={`question-card${isOpen ? " open" : ""}${isKeyboardActive ? " keyboard-active" : ""}${isMastered ? " mastered" : ""}`} id={question.id}>
      <div className="question-meta">
        <span className={`level-badge level-${question.level}`}>{question.level} · {question.level === "S" ? "必会" : "核心"}</span>
        {question.isRealInterview && <span className="real-badge">真实面经</span>}
        {question.tags.map((tag) => <span className="topic-badge" key={tag}>{tag}</span>)}
      </div>
      <div className="question-head-row">
        <button className="question-heading" data-question-id={question.id} type="button" onClick={onToggleOpen} onFocus={onFocus} aria-expanded={isOpen}>
          <span className="question-title-wrap">
            <span className="question-number">{String(index + 1).padStart(2, "0")}</span>
            {card?.titleHtml
              ? <span className="question-title" dangerouslySetInnerHTML={{ __html: card.titleHtml }} />
              : <span className="question-title">{displayPlain(question.title)}</span>}
          </span>
        </button>
        <div className="question-head-actions">
          <button
            type="button"
            className={`copy-question-btn${copiedKind === "prompt" ? " copied" : ""}`}
            onClick={onCopyPrompt}
            aria-label="复制题目，去问其他模型"
            title="复制题目，去问其他模型"
          >
            {copiedKind === "prompt" ? "已复制" : "复制题目"}
          </button>
          <button type="button" className="expand-icon" onClick={onToggleOpen} aria-hidden="true" tabIndex={-1}>
            {isOpen ? "−" : "+"}
          </button>
        </div>
      </div>
      {question.quick && (
        <div className={`quick-answer${isOpen ? "" : " compact"}`}>
          <span className="quick-kicker">30 秒口播</span>
          {card?.quickHtml
            ? <p dangerouslySetInnerHTML={{ __html: card.quickHtml }} />
            : <p>{displayPlain(question.quick)}</p>}
        </div>
      )}
      {isOpen && answer && (
        // eslint-disable-next-line jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events -- delegated <a class="question-link">
        <div
          className="answer-content"
          dangerouslySetInnerHTML={{ __html: answer }}
          onClick={(event) => {
            const node = event.target;
            const el = node instanceof Element ? node : node instanceof Node ? node.parentElement : null;
            const link = el?.closest("a.question-link");
            if (!(link instanceof HTMLAnchorElement)) return;
            if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
            const nextId = link.dataset.questionId;
            if (!nextId) return;
            event.preventDefault();
            const href = link.getAttribute("href") ?? "";
            const search = href.startsWith("?") ? href.slice(1) : href;
            onOpenQuestion(nextId, new URLSearchParams(search).get("book"));
          }}
        />
      )}
      {isOpen && !answer && <div className="answer-loading"><span />正在加载完整答案…</div>}
      <footer className="question-footer">
        <label>
          <input type="checkbox" checked={isMastered} onChange={onToggleMastered} />
          <span>{isMastered ? "已掌握" : "标记为已掌握"}</span>
        </label>
        <button type="button" onClick={onCopyLink}>{copiedKind === "link" ? "链接已复制" : "复制链接"}</button>
      </footer>
    </article>
  );
}

export const QuestionCard = memo(QuestionCardView);
