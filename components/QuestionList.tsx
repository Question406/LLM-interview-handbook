"use client";

import { useCallback, useLayoutEffect, useMemo, useRef, useState } from "react";
import type { HandbookQuestion, HandbookSection, QuestionCardHtml } from "@/content/types";
import { qualifiedId } from "@/lib/handbook";
import { QuestionCard, type CopiedKind } from "./QuestionCard";

const WINDOW_THRESHOLD = 24;
const ESTIMATE_CLOSED = 196;
const ESTIMATE_OPEN = 640;
const GAP = 12;
const OVERSCAN_PX = 1400;

export type QuestionListProps = {
  section: HandbookSection;
  handbookId: string;
  questions: HandbookQuestion[];
  openQuestions: ReadonlySet<string>;
  mastered: ReadonlySet<string>;
  focusedQuestionId: string | null;
  revealSolutions: boolean;
  copied: { id: string; kind: CopiedKind } | null;
  cards?: Record<string, QuestionCardHtml>;
  answers: Record<string, string>;
  scrollToId?: string | null;
  onScrolled?: () => void;
  onToggleOpen: (question: HandbookQuestion) => void;
  onToggleMastered: (questionId: string) => void;
  onCopyPrompt: (question: HandbookQuestion) => void;
  onCopyLink: (questionId: string) => void;
  onOpenQuestion: (questionId: string, book?: string | null) => void;
  onFocus: (questionId: string) => void;
  onNeedAnswer: (question: HandbookQuestion) => void;
  onNeedCards: (section: HandbookSection) => void;
};

function itemSize(question: HandbookQuestion, openQuestions: ReadonlySet<string>, measured: Record<string, number>) {
  if (measured[question.id]) return measured[question.id];
  return openQuestions.has(question.id) ? ESTIMATE_OPEN : ESTIMATE_CLOSED;
}

export function QuestionList(props: QuestionListProps) {
  const { questions, section, onNeedCards, scrollToId, onScrolled } = props;

  useLayoutEffect(() => {
    onNeedCards(section);
  }, [onNeedCards, section]);

  useLayoutEffect(() => {
    if (!scrollToId) return;
    if (!questions.some((question) => question.id === scrollToId)) return;
    const node = document.getElementById(scrollToId);
    if (!node) return;
    node.scrollIntoView({ behavior: "auto", block: "start" });
    onScrolled?.();
  }, [onScrolled, questions, scrollToId]);

  if (questions.length <= WINDOW_THRESHOLD) {
    return (
      <div className="question-list">
        {questions.map((question, index) => (
          <MountedQuestion key={question.id} {...props} question={question} index={index} />
        ))}
      </div>
    );
  }

  return <WindowedQuestionList {...props} />;
}

function WindowedQuestionList(props: QuestionListProps) {
  const { questions, openQuestions, scrollToId, focusedQuestionId } = props;
  const listRef = useRef<HTMLDivElement>(null);
  const [measured, setMeasured] = useState<Record<string, number>>({});
  const [viewport, setViewport] = useState({ top: 0, height: 900 });
  const [origin, setOrigin] = useState(0);

  const onSize = useCallback((id: string, height: number) => {
    const next = Math.max(1, Math.round(height));
    setMeasured((current) => (current[id] === next ? current : { ...current, [id]: next }));
  }, []);

  useLayoutEffect(() => {
    const update = () => {
      const node = listRef.current;
      if (!node) return;
      setOrigin(window.scrollY + node.getBoundingClientRect().top);
      setViewport({ top: window.scrollY, height: window.innerHeight });
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    return () => {
      window.removeEventListener("scroll", update);
      window.removeEventListener("resize", update);
    };
  }, [questions.length]);

  const layout = useMemo(() => questions.reduce<Array<{ question: HandbookQuestion; index: number; start: number; size: number }>>((items, question, index) => {
    const previous = items.at(-1);
    const start = previous ? previous.start + previous.size + GAP : 0;
    return [...items, { question, index, start, size: itemSize(question, openQuestions, measured) }];
  }, []), [measured, openQuestions, questions]);

  const totalHeight = layout.length ? layout[layout.length - 1].start + layout[layout.length - 1].size : 0;
  const viewStart = viewport.top - origin - OVERSCAN_PX;
  const viewEnd = viewport.top - origin + viewport.height + OVERSCAN_PX;
  const pinId = scrollToId || focusedQuestionId;
  const pinIndex = pinId ? questions.findIndex((question) => question.id === pinId) : -1;

  const visible = layout.filter((item, index) => {
    if (pinIndex >= 0 && Math.abs(index - pinIndex) <= 10) return true;
    return item.start + item.size >= viewStart && item.start <= viewEnd;
  });

  const first = visible[0];
  const last = visible[visible.length - 1];
  const padTop = first ? first.start : 0;
  const padBottom = last ? Math.max(0, totalHeight - (last.start + last.size)) : 0;

  useLayoutEffect(() => {
    if (!scrollToId) return;
    const item = layout.find((entry) => entry.question.id === scrollToId);
    const node = document.getElementById(scrollToId);
    if (node) return;
    if (item) window.scrollTo({ top: Math.max(0, origin + item.start - 128) });
  }, [layout, origin, scrollToId]);

  return (
    <div className="question-list question-list-windowed" ref={listRef}>
      <div className="question-list-spacer" style={{ height: padTop }} aria-hidden="true" />
      <div className="question-list-items">
        {visible.map((item) => (
          <MeasuredQuestion
            key={item.question.id}
            {...props}
            question={item.question}
            index={item.index}
            onSize={onSize}
          />
        ))}
      </div>
      <div className="question-list-spacer" style={{ height: padBottom }} aria-hidden="true" />
    </div>
  );
}

function MeasuredQuestion({
  question,
  onSize,
  ...rest
}: QuestionListProps & { question: HandbookQuestion; index: number; onSize: (id: string, height: number) => void }) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const node = ref.current;
    if (!node) return;
    const report = () => onSize(question.id, node.getBoundingClientRect().height);
    report();
    const observer = new ResizeObserver(report);
    observer.observe(node);
    return () => observer.disconnect();
  }, [onSize, question.id]);

  return (
    <div ref={ref} className="question-measure">
      <MountedQuestion {...rest} question={question} />
    </div>
  );
}

function MountedQuestion({
  question,
  index,
  handbookId,
  openQuestions,
  mastered,
  focusedQuestionId,
  revealSolutions,
  copied,
  cards,
  answers,
  onToggleOpen,
  onToggleMastered,
  onCopyPrompt,
  onCopyLink,
  onOpenQuestion,
  onFocus,
  onNeedAnswer,
}: QuestionListProps & { question: HandbookQuestion; index: number }) {
  const isOpen = openQuestions.has(question.id);

  useLayoutEffect(() => {
    if (isOpen) onNeedAnswer(question);
  }, [isOpen, onNeedAnswer, question]);

  return (
    <QuestionCard
      question={question}
      index={index}
      isOpen={isOpen}
      isMastered={mastered.has(qualifiedId(handbookId, question.id))}
      copiedKind={copied?.id === question.id ? copied.kind : null}
      isKeyboardActive={focusedQuestionId === question.id}
      revealSolutions={revealSolutions}
      card={cards?.[question.id]}
      answer={answers[qualifiedId(handbookId, question.id)]}
      onToggleOpen={() => onToggleOpen(question)}
      onToggleMastered={() => onToggleMastered(question.id)}
      onCopyPrompt={() => onCopyPrompt(question)}
      onCopyLink={() => onCopyLink(question.id)}
      onOpenQuestion={onOpenQuestion}
      onFocus={() => onFocus(question.id)}
    />
  );
}
