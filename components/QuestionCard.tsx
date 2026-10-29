"use client";

import { memo, useLayoutEffect, useMemo, useRef } from "react";
import type { HandbookQuestion, QuestionCardHtml } from "@/content/types";
import { displayPlain, writeClipboard } from "@/lib/handbook";
import { applyPracticeReveal, enhancePractice, handlePracticeClick, rememberTestsToggle } from "./practice-code";

export type CopiedKind = "link" | "prompt";

const openFollowups = new Map<string, Set<string>>();

function followupKey(details: HTMLDetailsElement) {
  return details.querySelector("summary")?.textContent?.trim() ?? "";
}

function AnswerContent({
  html,
  questionId,
  revealSolutions,
  onOpenQuestion,
}: {
  html: string;
  questionId: string;
  revealSolutions: boolean;
  onOpenQuestion: (questionId: string, book?: string | null) => void;
}) {
  const hostRef = useRef<HTMLDivElement>(null);
  // Stable object identity: React re-applies innerHTML whenever this prop object changes, which
  // would wipe the injected practice controls and open follow-ups on every rerender.
  const innerHtml = useMemo(() => ({ __html: html }), [html]);

  useLayoutEffect(() => {
    const node = hostRef.current;
    if (!node) return;

    enhancePractice(node, questionId);

    const saved = openFollowups.get(questionId);
    if (saved) {
      for (const details of node.querySelectorAll<HTMLDetailsElement>("details.followup")) {
        const key = followupKey(details);
        if (key && saved.has(key)) details.open = true;
      }
    }

    const onToggle = (event: Event) => {
      const details = event.target;
      if (!(details instanceof HTMLDetailsElement)) return;
      if (rememberTestsToggle(details, questionId) || !details.classList.contains("followup")) return;
      const key = followupKey(details);
      if (!key) return;
      const next = openFollowups.get(questionId) ?? new Set<string>();
      if (details.open) next.add(key);
      else next.delete(key);
      openFollowups.set(questionId, next);
    };

    node.addEventListener("toggle", onToggle, true);
    return () => node.removeEventListener("toggle", onToggle, true);
  }, [html, questionId]);

  useLayoutEffect(() => {
    const node = hostRef.current;
    if (!node) return;
    enhancePractice(node, questionId);
    applyPracticeReveal(node, questionId, revealSolutions);
  }, [html, questionId, revealSolutions]);

  return (
    // eslint-disable-next-line jsx-a11y/no-static-element-interactions, jsx-a11y/click-events-have-key-events -- delegated <a class="question-link"> and practice <button>s
    <div
      ref={hostRef}
      className="answer-content"
      dangerouslySetInnerHTML={innerHtml}
      onClick={(event) => {
        const node = event.target;
        const el = node instanceof Element ? node : node instanceof Node ? node.parentElement : null;
        if (el && hostRef.current && handlePracticeClick(el, hostRef.current, questionId, revealSolutions, writeClipboard)) return;
        const link = el?.closest("a.question-link");
        if (!(link instanceof HTMLAnchorElement)) return;
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
        const nextId = link.dataset.questionId;
        if (!nextId) return;
        event.preventDefault();
        event.stopPropagation();
        const href = link.getAttribute("href") ?? "";
        const search = href.startsWith("?") ? href.slice(1) : href;
        onOpenQuestion(nextId, new URLSearchParams(search).get("book"));
      }}
    />
  );
}

const MemoAnswerContent = memo(AnswerContent);

function clickTogglesCard(target: EventTarget | null) {
  const el = target instanceof Element ? target : target instanceof Node ? target.parentElement : null;
  if (!el) return false;
  return !el.closest("button, a, input, label, textarea, select, summary, .answer-content, .answer-loading");
}

function QuestionCardView({
  question,
  index,
  isOpen,
  isMastered,
  copiedKind,
  isKeyboardActive,
  revealSolutions,
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
  revealSolutions: boolean;
  card?: QuestionCardHtml;
  answer?: string;
  onToggleOpen: () => void;
  onToggleMastered: () => void;
  onCopyPrompt: () => void;
  onCopyLink: () => void;
  onOpenQuestion: (questionId: string, book?: string | null) => void;
  onFocus: () => void;
}) {
  const hasCodingPractice = question.tags.includes("完整编程练习");
  const canPractice = question.hasPractice === true;

  return (
    // eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/click-events-have-key-events -- heading button stays the keyboard control
    <article
      className={`question-card${isOpen ? " open" : ""}${isKeyboardActive ? " keyboard-active" : ""}${isMastered ? " mastered" : ""}`}
      id={question.id}
      onClick={(event) => {
        if (!clickTogglesCard(event.target)) return;
        if (window.getSelection()?.toString()) return;
        onToggleOpen();
      }}
    >
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
          {canPractice && <a className="copy-question-btn" href={`/practice?book=${encodeURIComponent(question.answerPath.split("/")[2] ?? "")}&section=${encodeURIComponent(question.sectionId)}&question=${encodeURIComponent(question.id)}&title=${encodeURIComponent(question.title)}`}>编程练习 ↗</a>}
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
      {question.quick && !question.collapseAnswer && (
        <div className={`quick-answer${isOpen ? "" : " compact"}`}>
          <span className="quick-kicker">{hasCodingPractice ? "编程题摘要 · 含完整实现与测试" : "30 秒口播"}</span>
          {card?.quickHtml
            ? <p dangerouslySetInnerHTML={{ __html: card.quickHtml }} />
            : <p>{displayPlain(question.quick)}</p>}
        </div>
      )}
      {hasCodingPractice && (
        <button type="button" className="coding-answer-toggle" onClick={onToggleOpen} aria-expanded={isOpen}>
          {isOpen ? "收起题面与代码答案" : "展开题面与代码答案 →"}
        </button>
      )}
      {isOpen && answer && (
        <MemoAnswerContent html={answer} questionId={question.id} revealSolutions={revealSolutions} onOpenQuestion={onOpenQuestion} />
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
