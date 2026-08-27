"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Handbook, HandbookCatalogEntry, HandbookQuestion, HandbookSection } from "@/content/types";
import { useContentLoader } from "@/hooks/useContentLoader";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { useMastered, useThemePreference } from "@/hooks/usePersistedUi";
import { findQuestionInHandbook, isTextEntryTarget, qualifiedId, questionPrompt, writeClipboard } from "@/lib/handbook";
import { filtersForHandbook, questionMatchesFilter, questionMatchesQuery, type FilterId } from "@/lib/handbook-filters";
import { EMPTY_SEARCH, parseHandbookSearch, resolveCatalogEntry, serializeHandbookSearch, type HandbookSearch } from "@/lib/handbook-route";
import { ContentGuide, EmptyState, ShortcutDialog } from "./ShellExtras";
import { Hero } from "./Hero";
import { QuestionList } from "./QuestionList";
import { Rail } from "./Rail";
import { StudyControls } from "./StudyControls";
import { Topbar } from "./Topbar";
import type { CopiedKind } from "./QuestionCard";

export function HandbookWorkspace({
  catalog,
  initialHandbook,
}: {
  catalog: HandbookCatalogEntry[];
  initialHandbook: Handbook;
}) {
  const { indexes, answers, cards, indexError, loadIndex, loadCards, loadAnswer } = useContentLoader(initialHandbook);
  const { mastered, toggleMastered } = useMastered();
  const { darkMode, toggleTheme } = useThemePreference();

  const [route, setRoute] = useState<HandbookSearch>(() => (
    typeof location === "undefined" ? EMPTY_SEARCH : parseHandbookSearch(location.search)
  ));
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<FilterId>("all");
  const [openQuestions, setOpenQuestions] = useState<Set<string>>(() => {
    const questionId = typeof location === "undefined" ? null : parseHandbookSearch(location.search).question;
    return new Set(questionId ? [questionId] : []);
  });
  const [focusedQuestionId, setFocusedQuestionId] = useState<string | null>(() => (
    typeof location === "undefined" ? null : parseHandbookSearch(location.search).question
  ));
  const [copied, setCopied] = useState<{ id: string; kind: CopiedKind } | null>(null);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [scrollToId, setScrollToId] = useState<string | null>(() => (
    typeof location === "undefined" ? null : parseHandbookSearch(location.search).question
  ));

  const searchRef = useRef<HTMLInputElement>(null);
  const keyboardStateRef = useRef<{
    shortcutsOpen: boolean;
    focusedQuestion?: HandbookQuestion;
    focusQuestion: (direction: 1 | -1) => void;
    goToAdjacentSection: (direction: 1 | -1) => void;
    toggleOpen: (question: HandbookQuestion) => void;
  } | null>(null);

  const debouncedQuery = useDebouncedValue(query, 180);
  const normalizedQuery = debouncedQuery.trim().toLocaleLowerCase();
  const isSearching = Boolean(normalizedQuery);

  const entry = resolveCatalogEntry(catalog, route.book) ?? catalog[0];
  const handbook = (entry && indexes[entry.id]) ?? initialHandbook;
  const handbookPending = Boolean(entry && !indexes[entry.id]);
  const activeSection = route.section;
  const guideOpen = route.view === "guide";

  const writeRoute = useCallback((next: HandbookSearch, mode: "push" | "replace" = "push") => {
    setRoute(next);
    const url = `${location.pathname}${serializeHandbookSearch(next, catalog)}`;
    history[`${mode}State`](null, "", url);
  }, [catalog]);

  useEffect(() => {
    const onPop = () => {
      const next = parseHandbookSearch(location.search);
      setRoute(next);
      setFocusedQuestionId(next.question);
      setScrollToId(next.question);
      if (next.question) setOpenQuestions((current) => new Set(current).add(next.question as string));
    };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    if (new URLSearchParams(location.search).get("book")) return;
    const nextUrl = `${location.pathname}${serializeHandbookSearch(route, catalog)}`;
    if (`${location.pathname}${location.search}` !== nextUrl) history.replaceState(null, "", nextUrl);
  }, [catalog, route]);

  useEffect(() => {
    const wanted = resolveCatalogEntry(catalog, route.book);
    if (wanted && !indexes[wanted.id]) void loadIndex(wanted);
  }, [catalog, indexes, loadIndex, route.book]);

  const openOverview = useCallback(() => {
    writeRoute({ book: handbook.slug, section: null, question: null, view: null });
    setFocusedQuestionId(null);
    setQuery("");
    setMobileNavOpen(false);
    window.scrollTo(0, 0);
  }, [handbook.slug, writeRoute]);

  const openGuide = useCallback(() => {
    writeRoute({ book: handbook.slug, section: null, question: null, view: "guide" });
    setFocusedQuestionId(null);
    setQuery("");
    setMobileNavOpen(false);
    window.scrollTo(0, 0);
  }, [handbook.slug, writeRoute]);

  const openSection = useCallback((sectionId: string) => {
    writeRoute({ book: handbook.slug, section: sectionId, question: null, view: null });
    setFocusedQuestionId(null);
    setQuery("");
    setMobileNavOpen(false);
    window.scrollTo(0, 0);
  }, [handbook.slug, writeRoute]);

  const goToQuestion = useCallback((questionId: string, book?: string | null) => {
    const targetEntry = resolveCatalogEntry(catalog, book) ?? entry;
    if (targetEntry && targetEntry.id !== handbook.id) {
      void loadIndex(targetEntry).then((loaded) => {
        if (!loaded) return;
        const found = findQuestionInHandbook(loaded, questionId);
        if (!found) return;
        writeRoute({ book: loaded.slug, section: found.section.id, question: found.question.id, view: null });
        setQuery("");
        setFilter("all");
        setLibraryOpen(false);
        setFocusedQuestionId(found.question.id);
        setOpenQuestions((current) => new Set(current).add(found.question.id));
        setScrollToId(found.question.id);
        void loadCards(found.section);
        void loadAnswer(loaded.id, found.question);
      });
      return;
    }
    const found = findQuestionInHandbook(handbook, questionId);
    if (!found) return;
    void loadCards(found.section);
    void loadAnswer(handbook.id, found.question);
    writeRoute({ book: handbook.slug, section: found.section.id, question: found.question.id, view: null });
    setFocusedQuestionId(found.question.id);
    setQuery("");
    setFilter("all");
    setOpenQuestions((current) => new Set(current).add(questionId));
    setScrollToId(questionId);
  }, [catalog, entry, handbook, loadAnswer, loadCards, loadIndex, writeRoute]);

  const switchHandbook = useCallback(async (nextId: string) => {
    const next = catalog.find((candidate) => candidate.id === nextId);
    if (!next) return;
    const loaded = indexes[next.id] ?? await loadIndex(next);
    if (!loaded) return;
    writeRoute({ book: loaded.slug, section: null, question: null, view: null }, "replace");
    setQuery("");
    setFilter("all");
    setOpenQuestions(new Set());
    setFocusedQuestionId(null);
    setLibraryOpen(false);
    window.scrollTo(0, 0);
  }, [catalog, indexes, loadIndex, writeRoute]);

  useEffect(() => {
    if (!route.question) return;
    const found = findQuestionInHandbook(handbook, route.question);
    if (!found) return;
    void loadCards(found.section);
    void loadAnswer(handbook.id, found.question);
  }, [handbook, loadAnswer, loadCards, route.question]);

  useEffect(() => {
    if (!activeSection) return;
    const section = handbook.sections.find((candidate) => candidate.id === activeSection);
    if (section) void loadCards(section);
  }, [activeSection, handbook, loadCards]);

  const availableFilters = useMemo(() => filtersForHandbook(handbook), [handbook]);
  const activeFilter = availableFilters.some((option) => option.id === filter) ? filter : "all";

  const visibleSections = useMemo(() => {
    const source = isSearching
      ? handbook.sections
      : handbook.sections.filter((section) => section.id === activeSection);
    return source.map((section) => ({
      ...section,
      questions: section.questions.filter((question) => (
        questionMatchesQuery(question, normalizedQuery)
        && questionMatchesFilter(question, activeFilter, handbook.id, mastered)
      )),
    })).filter((section) => section.questions.length > 0);
  }, [activeFilter, activeSection, handbook, isSearching, mastered, normalizedQuery]);

  const visibleQuestions = useMemo(
    () => visibleSections.flatMap((section) => section.questions),
    [visibleSections],
  );
  const isContentView = Boolean(activeSection) || isSearching;
  const masteredCount = handbook.sections.flatMap((section) => section.questions)
    .filter((question) => mastered.has(qualifiedId(handbook.id, question.id))).length;
  const progress = handbook.stats.questions ? (masteredCount / handbook.stats.questions) * 100 : 0;

  const toggleOpen = useCallback((question: HandbookQuestion) => {
    setOpenQuestions((current) => {
      const next = new Set(current);
      if (next.has(question.id)) next.delete(question.id); else next.add(question.id);
      return next;
    });
  }, []);

  const copyQuestionLink = useCallback(async (questionId: string) => {
    const found = findQuestionInHandbook(handbook, questionId);
    if (!found) return;
    const nextRoute = { book: handbook.slug, section: found.section.id, question: questionId, view: null } satisfies HandbookSearch;
    writeRoute(nextRoute, "replace");
    await writeClipboard(`${location.origin}${location.pathname}${serializeHandbookSearch(nextRoute, catalog)}`);
    setCopied({ id: questionId, kind: "link" });
    window.setTimeout(() => setCopied((current) => current?.id === questionId && current.kind === "link" ? null : current), 1100);
  }, [catalog, handbook, writeRoute]);

  const copyQuestionPrompt = useCallback(async (question: HandbookQuestion) => {
    const found = findQuestionInHandbook(handbook, question.id);
    if (!found) return;
    await writeClipboard(questionPrompt(question, found.section.title));
    setCopied({ id: question.id, kind: "prompt" });
    window.setTimeout(() => setCopied((current) => current?.id === question.id && current.kind === "prompt" ? null : current), 1100);
  }, [handbook]);

  const randomQuestion = () => {
    const pool = visibleQuestions.length ? visibleQuestions : handbook.sections.flatMap((section) => section.questions);
    const randomValue = window.crypto.getRandomValues(new Uint32Array(1))[0] / 2 ** 32;
    goToQuestion(pool[Math.floor(randomValue * pool.length)].id);
  };

  const focusQuestion = (direction: 1 | -1) => {
    if (!visibleQuestions.length) return;
    const currentIndex = focusedQuestionId ? visibleQuestions.findIndex((question) => question.id === focusedQuestionId) : -1;
    const startIndex = currentIndex === -1 ? (direction === 1 ? -1 : 0) : currentIndex;
    const nextIndex = (startIndex + direction + visibleQuestions.length) % visibleQuestions.length;
    const nextQuestion = visibleQuestions[nextIndex];
    void loadAnswer(handbook.id, nextQuestion);
    setFocusedQuestionId(nextQuestion.id);
    setOpenQuestions((current) => new Set(current).add(nextQuestion.id));
    setScrollToId(nextQuestion.id);
    window.requestAnimationFrame(() => {
      const heading = document.querySelector<HTMLButtonElement>(`button[data-question-id="${nextQuestion.id}"]`);
      heading?.focus({ preventScroll: true });
    });
  };

  const goToAdjacentSection = (direction: 1 | -1) => {
    const currentIndex = activeSection ? handbook.sections.findIndex((section) => section.id === activeSection) : -1;
    const startIndex = currentIndex === -1 ? (direction === 1 ? -1 : 0) : currentIndex;
    const nextIndex = (startIndex + direction + handbook.sections.length) % handbook.sections.length;
    openSection(handbook.sections[nextIndex].id);
  };

  const onNeedAnswer = useCallback((question: HandbookQuestion) => {
    void loadAnswer(handbook.id, question);
  }, [handbook.id, loadAnswer]);

  const onNeedCards = useCallback((section: HandbookSection) => {
    void loadCards(section);
  }, [loadCards]);

  const onScrolled = useCallback(() => {
    setScrollToId(null);
  }, []);

  const onToggleMastered = useCallback((questionId: string) => {
    toggleMastered(handbook.id, questionId);
  }, [handbook.id, toggleMastered]);

  useEffect(() => {
    keyboardStateRef.current = {
      shortcutsOpen,
      focusedQuestion: focusedQuestionId ? visibleQuestions.find((question) => question.id === focusedQuestionId) : undefined,
      focusQuestion,
      goToAdjacentSection,
      toggleOpen,
    };
  });

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setMobileNavOpen(false);
        setLibraryOpen(false);
        setShortcutsOpen(false);
        searchRef.current?.blur();
        return;
      }
      const keyboardState = keyboardStateRef.current;
      if (!keyboardState || isTextEntryTarget(event.target) || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey || keyboardState.shortcutsOpen) return;

      const { focusedQuestion } = keyboardState;
      switch (event.code) {
        case "ArrowUp":
          event.preventDefault();
          keyboardState.focusQuestion(-1);
          break;
        case "ArrowDown":
          event.preventDefault();
          keyboardState.focusQuestion(1);
          break;
        case "ArrowLeft":
          event.preventDefault();
          keyboardState.goToAdjacentSection(-1);
          break;
        case "ArrowRight":
          event.preventDefault();
          keyboardState.goToAdjacentSection(1);
          break;
        case "Enter":
          if (!focusedQuestion) break;
          event.preventDefault();
          keyboardState.toggleOpen(focusedQuestion);
          break;
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  const resultLabel = `${isContentView ? `${visibleQuestions.length} / ${handbook.stats.questions}` : handbook.stats.questions} 题`;

  return (
    <main className="app-shell">
      <Rail
        handbook={handbook}
        catalog={catalog}
        activeSection={activeSection}
        isSearching={isSearching}
        masteredCount={masteredCount}
        progress={progress}
        libraryOpen={libraryOpen}
        mobileNavOpen={mobileNavOpen}
        onOverview={openOverview}
        onToggleLibrary={() => setLibraryOpen((current) => !current)}
        onSwitchHandbook={(id) => void switchHandbook(id)}
        onOpenSection={openSection}
        onOpenGuide={openGuide}
        onCloseMobile={() => setMobileNavOpen(false)}
      />
      {mobileNavOpen && <button className="nav-backdrop" type="button" onClick={() => setMobileNavOpen(false)} aria-label="关闭导航" />}
      {shortcutsOpen && <ShortcutDialog onClose={() => setShortcutsOpen(false)} />}

      <section className="workspace" id="top">
        <Topbar
          query={query}
          resultLabel={resultLabel}
          darkMode={darkMode}
          searchRef={searchRef}
          onQueryChange={setQuery}
          onClearQuery={() => setQuery("")}
          onOpenMobile={() => setMobileNavOpen(true)}
          onOpenShortcuts={() => setShortcutsOpen(true)}
          onToggleTheme={toggleTheme}
        />

        <div className="page-wrap">
          {indexError && <EmptyState title="手册加载失败" detail={indexError} />}
          {handbookPending && <div className="answer-loading"><span />正在加载题库…</div>}
          {!handbookPending && !isContentView && !guideOpen && (
            <Hero
              handbook={handbook}
              masteredCount={masteredCount}
              mastered={mastered}
              onOpenSection={openSection}
              onRandomQuestion={randomQuestion}
            />
          )}

          {!handbookPending && isContentView && (
            <StudyControls
              filters={availableFilters}
              filter={activeFilter}
              onFilter={setFilter}
              onExpandVisible={() => setOpenQuestions(new Set(visibleQuestions.map((question) => question.id)))}
              onCollapseAll={() => setOpenQuestions(new Set())}
            />
          )}

          {!handbookPending && isContentView && (
            <div className="question-sections">
              {isSearching && (
                <header className="search-results-intro">
                  <div>
                    <div className="eyebrow"><span /> 检索</div>
                    <h2>“{debouncedQuery.trim()}”</h2>
                  </div>
                  <div className="section-count">{visibleQuestions.length} 题</div>
                </header>
              )}
              {visibleSections.map((section) => (
                <section className="question-section" key={section.id}>
                  <header className="section-intro">
                    <div>
                      <div className="eyebrow"><span /> {String(handbook.sections.findIndex((candidate) => candidate.id === section.id) + 1).padStart(2, "0")}</div>
                      <h2>{section.title}</h2>
                      <p>{section.description}</p>
                    </div>
                    <div className="section-count">{section.questions.length} 题</div>
                  </header>
                  <QuestionList
                    section={section}
                    handbookId={handbook.id}
                    questions={section.questions}
                    openQuestions={openQuestions}
                    mastered={mastered}
                    focusedQuestionId={focusedQuestionId}
                    copied={copied}
                    cards={cards[section.cardsPath]}
                    answers={answers}
                    scrollToId={scrollToId && section.questions.some((question) => question.id === scrollToId) ? scrollToId : null}
                    onScrolled={onScrolled}
                    onToggleOpen={toggleOpen}
                    onToggleMastered={onToggleMastered}
                    onCopyPrompt={copyQuestionPrompt}
                    onCopyLink={copyQuestionLink}
                    onOpenQuestion={goToQuestion}
                    onFocus={setFocusedQuestionId}
                    onNeedAnswer={onNeedAnswer}
                    onNeedCards={onNeedCards}
                  />
                </section>
              ))}
              {visibleSections.length === 0 && (
                <EmptyState
                  title="没有找到匹配的题目"
                  detail="试试换一个关键词，或清除当前筛选。"
                  action={{ label: "清除条件", onClick: () => { setQuery(""); setFilter("all"); } }}
                />
              )}
            </div>
          )}

          {!handbookPending && !isContentView && guideOpen && <ContentGuide onOverview={openOverview} />}
        </div>
      </section>
    </main>
  );
}
