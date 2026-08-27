"use client";

import { useCallback, useRef, useState } from "react";
import type { Handbook, HandbookCatalogEntry, HandbookQuestion, HandbookSection, QuestionCardHtml } from "@/content/types";
import { validateHandbook } from "@/content/validate";
import { fetchJson, qualifiedId } from "@/lib/handbook";

export function useContentLoader(initialHandbook: Handbook) {
  const [indexes, setIndexes] = useState<Record<string, Handbook>>({ [initialHandbook.id]: initialHandbook });
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [cards, setCards] = useState<Record<string, Record<string, QuestionCardHtml>>>({});
  const [indexError, setIndexError] = useState<string | null>(null);
  const jsonPromises = useRef(new Map<string, Promise<unknown>>());
  const answersRef = useRef<Record<string, string>>({});
  const cardsRef = useRef<Record<string, Record<string, QuestionCardHtml>>>({});
  const indexesRef = useRef<Record<string, Handbook>>({ [initialHandbook.id]: initialHandbook });

  const loadJson = useCallback(<T,>(path: string, loader: () => Promise<T>) => {
    const existing = jsonPromises.current.get(path) as Promise<T> | undefined;
    if (existing) return existing;
    const request = loader();
    jsonPromises.current.set(path, request);
    return request;
  }, []);

  const loadIndex = useCallback(async (entry: HandbookCatalogEntry) => {
    const cached = indexesRef.current[entry.id];
    if (cached) return cached;
    try {
      const next = validateHandbook(await loadJson(entry.indexPath, () => fetchJson<Handbook>(entry.indexPath)));
      indexesRef.current = indexesRef.current[next.id] ? indexesRef.current : { ...indexesRef.current, [next.id]: next };
      setIndexes(indexesRef.current);
      return indexesRef.current[next.id];
    } catch (error: unknown) {
      jsonPromises.current.delete(entry.indexPath);
      setIndexError(error instanceof Error ? error.message : "手册索引加载失败");
      return undefined;
    }
  }, [loadJson]);

  const loadCards = useCallback(async (section: HandbookSection) => {
    if (cardsRef.current[section.cardsPath]) return;
    try {
      const chunk = await loadJson(section.cardsPath, () => fetchJson<Record<string, QuestionCardHtml>>(section.cardsPath));
      if (cardsRef.current[section.cardsPath]) return;
      cardsRef.current = { ...cardsRef.current, [section.cardsPath]: chunk };
      setCards(cardsRef.current);
    } catch {
      jsonPromises.current.delete(section.cardsPath);
    }
  }, [loadJson]);

  const loadAnswer = useCallback(async (handbookId: string, question: HandbookQuestion) => {
    const key = qualifiedId(handbookId, question.id);
    if (answersRef.current[key]) return;
    try {
      const html = await loadJson(question.answerPath, () => fetchJson<string>(question.answerPath));
      if (answersRef.current[key]) return;
      answersRef.current = { ...answersRef.current, [key]: html };
      setAnswers(answersRef.current);
    } catch {
      jsonPromises.current.delete(question.answerPath);
    }
  }, [loadJson]);

  return { indexes, answers, cards, indexError, loadIndex, loadCards, loadAnswer };
}
