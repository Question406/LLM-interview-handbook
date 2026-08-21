"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { Handbook, HandbookQuestion } from "@/content/types";
import { sortHandbooks, validateHandbook } from "@/content/validate";

type Filter = "all" | "S" | "A" | "mastered" | "unmastered" | "real";

const STORAGE_KEY = "interview-atlas-mastered-v1";
const THEME_KEY = "interview-atlas-theme";

function qualifiedId(handbookId: string, questionId: string) {
  return `${handbookId}/${questionId}`;
}

function isTextEntryTarget(target: EventTarget | null) {
  return target instanceof HTMLInputElement
    || target instanceof HTMLTextAreaElement
    || (target instanceof HTMLElement && target.isContentEditable);
}

type CopiedKind = "link" | "prompt";

function questionPrompt(question: HandbookQuestion, sectionTitle: string) {
  const context = [
    sectionTitle.replace(/^\d+\s*·\s*/, ""),
    `${question.level} 级`,
    question.isRealInterview ? "真实面经" : "",
    ...question.tags,
  ].filter(Boolean).join(" · ");
  return [
    "请作为资深面试官，把下面这道题讲透：先给定义和核心结论，再讲适用条件、一个具体例子、常见追问与易错点。公式用 LaTeX。",
    "",
    context,
    `题目：${question.title}`,
  ].join("\n");
}

async function writeClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    area.remove();
  }
}

function QuestionCard({
  question,
  index,
  isOpen,
  isMastered,
  copiedKind,
  isKeyboardActive,
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
  answer?: string;
  onToggleOpen: () => void;
  onToggleMastered: () => void;
  onCopyPrompt: () => void;
  onCopyLink: () => void;
  onOpenQuestion: (questionId: string) => void;
  onFocus: () => void;
}) {
  return (
    <article className={`question-card${isOpen ? " open" : ""}${isKeyboardActive ? " keyboard-active" : ""}`} id={question.id}>
      <div className="question-meta">
        <span className={`level-badge level-${question.level}`}>{question.level} · {question.level === "S" ? "MUST KNOW" : "CORE"}</span>
        {question.isRealInterview && <span className="real-badge">真实面经</span>}
        {question.tags.map((tag) => <span className="topic-badge" key={tag}>{tag}</span>)}
      </div>
      <div className="question-head-row">
        <button className="question-heading" data-question-id={question.id} type="button" onClick={onToggleOpen} onFocus={onFocus} aria-expanded={isOpen}>
          <span className="question-title-wrap">
            <span className="question-number">{String(index + 1).padStart(2, "0")}</span>
            <span className="question-title" dangerouslySetInnerHTML={{ __html: question.titleHtml }} />
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
            {copiedKind === "prompt" ? "已复制 ✓" : "复制题目"}
          </button>
          <button type="button" className="expand-icon" onClick={onToggleOpen} aria-hidden="true" tabIndex={-1}>
            {isOpen ? "↑" : "↘"}
          </button>
        </div>
      </div>
      {!isOpen && question.quick && (
        <div className="quick-answer compact">
          <span>30 秒回答</span>
          <p dangerouslySetInnerHTML={{ __html: question.quickHtml }} />
        </div>
      )}
      {isOpen && answer && (
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
            onOpenQuestion(nextId);
          }}
        />
      )}
      {isOpen && !answer && <div className="answer-loading"><span />正在加载完整答案…</div>}
      <footer className="question-footer">
        <label>
          <input type="checkbox" checked={isMastered} onChange={onToggleMastered} />
          <span>{isMastered ? "已掌握" : "标记为已掌握"}</span>
        </label>
        <button type="button" onClick={onCopyLink}>{copiedKind === "link" ? "链接已复制 ✓" : "复制链接 #"}</button>
      </footer>
    </article>
  );
}

function HandbookWorkspace({ handbooks }: { handbooks: Handbook[] }) {
  const [handbookId, setHandbookId] = useState(handbooks[0].id);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [mastered, setMastered] = useState<Set<string>>(new Set());
  const [openQuestions, setOpenQuestions] = useState<Set<string>>(new Set());
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [guideOpen, setGuideOpen] = useState(false);
  const [shortcutsOpen, setShortcutsOpen] = useState(false);
  const [focusedQuestionId, setFocusedQuestionId] = useState<string | null>(null);
  const [copied, setCopied] = useState<{ id: string; kind: CopiedKind } | null>(null);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [answerChunks, setAnswerChunks] = useState<Record<string, Record<string, string>>>({});
  const searchRef = useRef<HTMLInputElement>(null);
  const chunkPromises = useRef(new Map<string, Promise<Record<string, string>>>());
  const pendingScrollRef = useRef<string | null>(null);
  const keyboardStateRef = useRef<{
    shortcutsOpen: boolean;
    focusedQuestion?: HandbookQuestion;
    focusQuestion: (direction: 1 | -1) => void;
    goToAdjacentSection: (direction: 1 | -1) => void;
    toggleOpen: (question: HandbookQuestion) => void;
  } | null>(null);

  const handbook = handbooks.find((candidate) => candidate.id === handbookId) ?? handbooks[0];

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
        setMastered(new Set(Array.isArray(stored) ? stored : []));
        const savedTheme = localStorage.getItem(THEME_KEY);
        const shouldUseDark = savedTheme === "dark" || (!savedTheme && matchMedia("(prefers-color-scheme: dark)").matches);
        setDarkMode(shouldUseDark);
        document.documentElement.dataset.theme = shouldUseDark ? "dark" : "light";
      } catch {
        setMastered(new Set());
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    const applyLocation = () => {
      const params = new URLSearchParams(location.search);
      const questionId = params.get("question");
      const question = handbook.sections.flatMap((section) => section.questions).find((candidate) => candidate.id === questionId);
      const sectionId = question
        ? handbook.sections.find((section) => section.questions.some((candidate) => candidate.id === question.id))?.id
        : params.get("section");

      if (sectionId && handbook.sections.some((section) => section.id === sectionId)) {
        setActiveSection(sectionId);
        setGuideOpen(false);
      } else {
        setActiveSection(null);
        setGuideOpen(params.get("view") === "guide");
      }

      if (!question) return;
      setQuery("");
      setFilter("all");
      setFocusedQuestionId(question.id);
      setOpenQuestions((current) => new Set(current).add(question.id));
      pendingScrollRef.current = question.id;
      let request = chunkPromises.current.get(question.answerPath);
      if (!request) {
        request = fetch(question.answerPath).then((response) => response.json() as Promise<Record<string, string>>);
        chunkPromises.current.set(question.answerPath, request);
      }
      void request.then((chunk) => setAnswerChunks((current) => ({ ...current, [question.answerPath]: chunk })));
    };

    applyLocation();
    window.addEventListener("popstate", applyLocation);
    return () => window.removeEventListener("popstate", applyLocation);
  }, [handbook]);

  const normalizedQuery = query.trim().toLocaleLowerCase();
  const isSearching = Boolean(normalizedQuery);
  const sectionsInView = isSearching
    ? handbook.sections
    : handbook.sections.filter((section) => section.id === activeSection);
  const visibleSections = useMemo(() => sectionsInView.map((section) => ({
    ...section,
    questions: section.questions.filter((question) => {
      const questionKey = qualifiedId(handbook.id, question.id);
      const matchesSearch = !normalizedQuery || `${question.title} ${question.quick} ${question.tags.join(" ")} ${question.searchText}`.toLocaleLowerCase().includes(normalizedQuery);
      const matchesFilter = filter === "all"
        || question.level === filter
        || (filter === "mastered" && mastered.has(questionKey))
        || (filter === "unmastered" && !mastered.has(questionKey))
        || (filter === "real" && question.isRealInterview);
      return matchesSearch && matchesFilter;
    }),
  })).filter((section) => section.questions.length > 0), [filter, handbook, mastered, normalizedQuery, sectionsInView]);

  const visibleQuestions = visibleSections.flatMap((section) => section.questions);
  const isContentView = Boolean(activeSection) || isSearching;

  useEffect(() => {
    const questionId = pendingScrollRef.current;
    if (!questionId || !visibleQuestions.some((question) => question.id === questionId)) return;
    const node = document.getElementById(questionId);
    if (!node) return;
    pendingScrollRef.current = null;
    node.scrollIntoView({ behavior: "auto", block: "start" });
  }, [focusedQuestionId, openQuestions, visibleQuestions]);
  const masteredCount = handbook.sections.flatMap((section) => section.questions)
    .filter((question) => mastered.has(qualifiedId(handbook.id, question.id))).length;
  const progress = handbook.stats.questions ? (masteredCount / handbook.stats.questions) * 100 : 0;

  const toggleMastered = (questionId: string) => {
    const key = qualifiedId(handbook.id, questionId);
    setMastered((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key); else next.add(key);
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...next]));
      return next;
    });
  };

  const loadAnswer = async (question: HandbookQuestion) => {
    if (answerChunks[question.answerPath]) return;
    let request = chunkPromises.current.get(question.answerPath);
    if (!request) {
      request = fetch(question.answerPath).then((response) => {
        if (!response.ok) throw new Error(`Could not load ${question.answerPath}`);
        return response.json() as Promise<Record<string, string>>;
      });
      chunkPromises.current.set(question.answerPath, request);
    }
    try {
      const chunk = await request;
      setAnswerChunks((current) => current[question.answerPath] ? current : { ...current, [question.answerPath]: chunk });
    } catch {
      chunkPromises.current.delete(question.answerPath);
    }
  };

  const toggleOpen = (question: HandbookQuestion) => {
    if (!openQuestions.has(question.id)) void loadAnswer(question);
    setOpenQuestions((current) => {
      const next = new Set(current);
      if (next.has(question.id)) next.delete(question.id); else next.add(question.id);
      return next;
    });
  };

  const setRoute = (params: URLSearchParams, mode: "push" | "replace" = "push") => {
    const nextUrl = `${location.pathname}${params.size ? `?${params.toString()}` : ""}`;
    history[`${mode}State`](null, "", nextUrl);
  };

  const openOverview = () => {
    setActiveSection(null);
    setGuideOpen(false);
    setFocusedQuestionId(null);
    setQuery("");
    setMobileNavOpen(false);
    setRoute(new URLSearchParams());
    window.scrollTo(0, 0);
  };

  const openGuide = () => {
    setActiveSection(null);
    setGuideOpen(true);
    setFocusedQuestionId(null);
    setQuery("");
    setMobileNavOpen(false);
    setRoute(new URLSearchParams({ view: "guide" }));
    window.scrollTo(0, 0);
  };

  const openSection = (sectionId: string) => {
    setActiveSection(sectionId);
    setGuideOpen(false);
    setFocusedQuestionId(null);
    setQuery("");
    setMobileNavOpen(false);
    setRoute(new URLSearchParams({ section: sectionId }));
    window.scrollTo(0, 0);
  };

  const goToQuestion = (questionId: string) => {
    const question = handbook.sections.flatMap((section) => section.questions).find((candidate) => candidate.id === questionId);
    const section = handbook.sections.find((candidate) => candidate.questions.some((item) => item.id === questionId));
    if (!question || !section) return;
    void loadAnswer(question);
    setActiveSection(section.id);
    setGuideOpen(false);
    setFocusedQuestionId(question.id);
    setQuery("");
    setFilter("all");
    setOpenQuestions((current) => new Set(current).add(questionId));
    setRoute(new URLSearchParams({ section: section.id, question: question.id }));
    pendingScrollRef.current = questionId;
  };

  const copyQuestionLink = async (questionId: string) => {
    const section = handbook.sections.find((candidate) => candidate.questions.some((question) => question.id === questionId));
    if (!section) return;
    const params = new URLSearchParams({ section: section.id, question: questionId });
    const url = `${location.origin}${location.pathname}?${params.toString()}`;
    setRoute(params, "replace");
    await writeClipboard(url);
    setCopied({ id: questionId, kind: "link" });
    window.setTimeout(() => setCopied((current) => current?.id === questionId && current.kind === "link" ? null : current), 1100);
  };

  const copyQuestionPrompt = async (question: HandbookQuestion) => {
    const section = handbook.sections.find((candidate) => candidate.questions.some((item) => item.id === question.id));
    if (!section) return;
    await writeClipboard(questionPrompt(question, section.title));
    setCopied({ id: question.id, kind: "prompt" });
    window.setTimeout(() => setCopied((current) => current?.id === question.id && current.kind === "prompt" ? null : current), 1100);
  };

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
    void loadAnswer(nextQuestion);
    setFocusedQuestionId(nextQuestion.id);
    setOpenQuestions((current) => new Set(current).add(nextQuestion.id));
    window.requestAnimationFrame(() => {
      const heading = document.querySelector<HTMLButtonElement>(`button[data-question-id="${nextQuestion.id}"]`);
      heading?.focus({ preventScroll: true });
      heading?.scrollIntoView({ behavior: "auto", block: "center" });
    });
  };

  const goToAdjacentSection = (direction: 1 | -1) => {
    const currentIndex = activeSection ? handbook.sections.findIndex((section) => section.id === activeSection) : -1;
    const startIndex = currentIndex === -1 ? (direction === 1 ? -1 : 0) : currentIndex;
    const nextIndex = (startIndex + direction + handbook.sections.length) % handbook.sections.length;
    openSection(handbook.sections[nextIndex].id);
  };

  const switchHandbook = (nextId: string) => {
    const next = handbooks.find((candidate) => candidate.id === nextId);
    if (!next) return;
    setHandbookId(nextId);
    setQuery("");
    setFilter("all");
    setOpenQuestions(new Set());
    setActiveSection(null);
    setGuideOpen(false);
    setFocusedQuestionId(null);
    setLibraryOpen(false);
    history.replaceState(null, "", location.pathname);
    window.scrollTo(0, 0);
  };

  const toggleTheme = () => {
    setDarkMode((current) => {
      const next = !current;
      document.documentElement.dataset.theme = next ? "dark" : "light";
      localStorage.setItem(THEME_KEY, next ? "dark" : "light");
      return next;
    });
  };

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

  return (
    <main className="app-shell">
      <aside className={`rail${mobileNavOpen ? " mobile-open" : ""}`}>
        <div className="rail-head">
          <button className="wordmark" type="button" onClick={openOverview}>
            <span className="wordmark-mark">IA</span><span>Interview Atlas</span>
          </button>
          <button className="mobile-close" type="button" onClick={() => setMobileNavOpen(false)} aria-label="关闭导航">×</button>
        </div>

        <div className="library-switcher">
          <button type="button" onClick={() => setLibraryOpen((current) => !current)} aria-expanded={libraryOpen}>
            <span><small>当前资料</small><b>{handbook.shortTitle}</b></span><span>{libraryOpen ? "−" : "+"}</span>
          </button>
          {libraryOpen && <div className="library-menu">
            {handbooks.map((candidate) => (
              <button type="button" className={candidate.id === handbook.id ? "active" : ""} key={candidate.id} onClick={() => switchHandbook(candidate.id)}>
                <span>{candidate.shortTitle}</span><small>{candidate.stats.questions} 题</small>
              </button>
            ))}
          </div>}
        </div>

        <div className="rail-label">手册目录</div>
        <nav className="module-nav" aria-label="手册目录">
          {handbook.sections.map((section, index) => (
            <button className={activeSection === section.id && !isSearching ? "module-link active" : "module-link"} type="button" key={section.id} onClick={() => openSection(section.id)}>
              <span className="module-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="module-name">{section.title.replace(/^\d+\s*·\s*/, "")}</span>
              <span className="module-count">{section.questions.length}</span>
            </button>
          ))}
        </nav>
        <button className="add-content" type="button" onClick={openGuide}><span>+</span> 以后怎么加资料</button>
        <div className="rail-progress">
          <div><span>复习进度</span><b>{masteredCount} / {handbook.stats.questions}</b></div>
          <div className="progress-track"><span style={{ width: `${progress}%` }} /></div>
          <p>{masteredCount ? `已经掌握 ${Math.round(progress)}%，继续保持。` : "每掌握一题，这里就会向前一点。"}</p>
        </div>
      </aside>
      {mobileNavOpen && <button className="nav-backdrop" type="button" onClick={() => setMobileNavOpen(false)} aria-label="关闭导航" />}
      {shortcutsOpen && <div className="shortcut-layer" role="presentation">
        <button className="shortcut-backdrop" type="button" onClick={() => setShortcutsOpen(false)} aria-label="关闭快捷键说明" />
        <section className="shortcut-dialog" role="dialog" aria-modal="true" aria-labelledby="shortcut-title">
          <header><div><div className="eyebrow"><span /> KEYBOARD</div><h2 id="shortcut-title">键盘快捷键</h2></div><button type="button" onClick={() => setShortcutsOpen(false)} aria-label="关闭快捷键说明">×</button></header>
          <dl>
            <div><dt><kbd>↑</kbd> <kbd>↓</kbd></dt><dd>上一题 / 下一题</dd></div>
            <div><dt><kbd>←</kbd> <kbd>→</kbd></dt><dd>上一个 / 下一个模块</dd></div>
            <div><dt><kbd>Enter</kbd></dt><dd>展开或折叠当前题</dd></div>
            <div><dt><kbd>Esc</kbd></dt><dd>关闭面板</dd></div>
          </dl>
        </section>
      </div>}

      <section className="workspace" id="top">
        <header className="topbar">
          <button className="mobile-menu" type="button" onClick={() => setMobileNavOpen(true)} aria-label="打开导航">☰</button>
          <label className="search-field">
            <span aria-hidden="true">⌕</span>
            <input ref={searchRef} value={query} onChange={(event) => setQuery(event.target.value)} type="search" placeholder="搜索 DPO、Skill、ZeRO 或某家公司…" aria-label="搜索手册" />
            {query && <button type="button" onClick={() => setQuery("")} aria-label="清除搜索">×</button>}
          </label>
          <span className="result-count">{isContentView ? `${visibleQuestions.length} / ${handbook.stats.questions}` : handbook.stats.questions} 题</span>
          <button className="icon-button shortcut-button" type="button" onClick={() => setShortcutsOpen(true)} aria-label="查看键盘快捷键">?</button>
          <button className="icon-button" type="button" onClick={toggleTheme} aria-label="切换主题">{darkMode ? "☀" : "◐"}</button>
        </header>

        <div className="page-wrap">
          {!isContentView && !guideOpen && <section className="hero">
            <div className="hero-copy">
              <div className="eyebrow"><span /> {handbook.edition} · INTERVIEW HANDBOOK</div>
              <h1>把知识点，<br />变成你的<span>面试反射</span>。</h1>
              <p>{handbook.description}</p>
              <div className="audience-line">{handbook.audience}</div>
              <div className="hero-actions">
                <button type="button" className="primary-action" onClick={() => openSection(handbook.sections[0].id)}>继续复习 <span>→</span></button>
                <button type="button" className="secondary-action" onClick={randomQuestion}>随机抽一题</button>
              </div>
            </div>
            <div className="hero-card" aria-label="手册数据摘要">
              <div className="orbit orbit-one" /><div className="orbit orbit-two" />
              <div className="score-disc"><b>{handbook.stats.questions}</b><span>题库</span></div>
              <div className="metric metric-a"><b>{handbook.stats.mustKnow}</b><span>S 级核心题</span></div>
              <div className="metric metric-b"><b>{handbook.sections.length}</b><span>知识模块</span></div>
              <div className="metric metric-c"><b>{handbook.stats.sources}</b><span>原始来源</span></div>
            </div>
          </section>}

          {isContentView && <section className="study-controls" aria-label="复习筛选">
            <div className="filter-row">
              {([
                ["all", "全部"], ["S", "S 级"], ["A", "A 级"], ["real", "真实面经"], ["mastered", "已掌握"], ["unmastered", "未掌握"],
              ] as [Filter, string][]).map(([value, label]) => <button className={filter === value ? "active" : ""} type="button" key={value} onClick={() => setFilter(value)}>{label}</button>)}
            </div>
            <div className="bulk-actions">
              <button type="button" onClick={() => { visibleQuestions.forEach((question) => void loadAnswer(question)); setOpenQuestions(new Set(visibleQuestions.map((question) => question.id))); }}>全部展开</button>
              <button type="button" onClick={() => setOpenQuestions(new Set())}>全部折叠</button>
            </div>
          </section>}

          {isContentView && <div className="question-sections">
            {isSearching && <header className="search-results-intro"><div><div className="eyebrow"><span /> SEARCH RESULTS</div><h2>“{query.trim()}” 的检索结果</h2></div><div className="section-count">{visibleQuestions.length} 题</div></header>}
            {visibleSections.map((section) => (
              <section className="question-section" key={section.id}>
                <header className="section-intro">
                  <div>
                    <div className="eyebrow"><span /> MODULE {String(handbook.sections.findIndex((candidate) => candidate.id === section.id) + 1).padStart(2, "0")}</div>
                    <h2>{section.title}</h2>
                    <p>{section.description}</p>
                  </div>
                  <div className="section-count">{section.questions.length} 题</div>
                </header>
                <div className="question-list">
                  {section.questions.map((question, questionIndex) => (
                    <QuestionCard
                      key={question.id}
                      question={question}
                      index={questionIndex}
                      isOpen={openQuestions.has(question.id)}
                      isMastered={mastered.has(qualifiedId(handbook.id, question.id))}
                      copiedKind={copied?.id === question.id ? copied.kind : null}
                      isKeyboardActive={focusedQuestionId === question.id}
                      answer={answerChunks[question.answerPath]?.[question.id]}
                      onToggleOpen={() => toggleOpen(question)}
                      onToggleMastered={() => toggleMastered(question.id)}
                      onCopyPrompt={() => copyQuestionPrompt(question)}
                      onCopyLink={() => copyQuestionLink(question.id)}
                      onOpenQuestion={goToQuestion}
                      onFocus={() => setFocusedQuestionId(question.id)}
                    />
                  ))}
                </div>
              </section>
            ))}
            {visibleSections.length === 0 && <div className="empty-state"><b>没有找到匹配的题目</b><p>试试换一个关键词，或清除当前筛选。</p><button type="button" onClick={() => { setQuery(""); setFilter("all"); }}>清除条件</button></div>}
          </div>}

          {!isContentView && guideOpen && <section className="content-guide">
            <div className="guide-number">+N</div>
            <div><div className="eyebrow"><span /> CONTENT FIRST</div><h2>新资料只需要进内容层。</h2></div>
            <p>页面、搜索、筛选、复习进度都由通用组件负责。以后每新增一题，只需要放入一个独立 Markdown 文件；构建器会自动汇总、校验并生成资料库。</p>
            <button type="button" onClick={openOverview}>回到首页 ↑</button>
          </section>}
        </div>
      </section>
    </main>
  );
}

export default function HandbookApp() {
  const [handbooks, setHandbooks] = useState<Handbook[] | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/content/registry.json")
      .then((response) => {
        if (!response.ok) throw new Error(`手册索引加载失败（${response.status}）`);
        return response.json() as Promise<Handbook[]>;
      })
      .then((data) => {
        const next = sortHandbooks(data.map(validateHandbook));
        if (!cancelled) setHandbooks(next);
      })
      .catch((error: unknown) => {
        if (!cancelled) setLoadError(error instanceof Error ? error.message : "手册索引加载失败");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (loadError) {
    return (
      <main className="app-shell">
        <section className="workspace">
          <div className="page-wrap">
            <div className="empty-state">
              <b>手册暂时打不开</b>
              <p>{loadError}</p>
            </div>
          </div>
        </section>
      </main>
    );
  }

  if (!handbooks) {
    return (
      <main className="app-shell">
        <section className="workspace">
          <div className="page-wrap">
            <div className="answer-loading"><span />正在加载题库…</div>
          </div>
        </section>
      </main>
    );
  }

  return <HandbookWorkspace handbooks={handbooks} />;
}
