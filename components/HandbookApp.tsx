"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { handbooks } from "@/content/registry";
import type { HandbookQuestion } from "@/content/types";

type Filter = "all" | "S" | "A" | "mastered" | "unmastered" | "real";

const STORAGE_KEY = "interview-atlas-mastered-v1";
const THEME_KEY = "interview-atlas-theme";

function qualifiedId(handbookId: string, questionId: string) {
  return `${handbookId}/${questionId}`;
}

function QuestionCard({
  question,
  index,
  isOpen,
  isMastered,
  copied,
  answer,
  onToggleOpen,
  onToggleMastered,
  onCopy,
}: {
  question: HandbookQuestion;
  index: number;
  isOpen: boolean;
  isMastered: boolean;
  copied: boolean;
  answer?: string;
  onToggleOpen: () => void;
  onToggleMastered: () => void;
  onCopy: () => void;
}) {
  return (
    <article className={`question-card${isOpen ? " open" : ""}`} id={question.id}>
      <div className="question-meta">
        <span className={`level-badge level-${question.level}`}>{question.level} · {question.level === "S" ? "MUST KNOW" : "CORE"}</span>
        {question.isRealInterview && <span className="real-badge">真实面经</span>}
        {question.tags.map((tag) => <span className="topic-badge" key={tag}>{tag}</span>)}
      </div>
      <button className="question-heading" type="button" onClick={onToggleOpen} aria-expanded={isOpen}>
        <span className="question-title-wrap">
          <span className="question-number">{String(index + 1).padStart(2, "0")}</span>
          <span className="question-title">{question.title}</span>
        </span>
        <span className="expand-icon" aria-hidden="true">{isOpen ? "↑" : "↘"}</span>
      </button>
      {!isOpen && question.quick && (
        <div className="quick-answer compact">
          <span>30 秒回答</span>
          <p>{question.quick}</p>
        </div>
      )}
      {isOpen && answer && <div className="answer-content" dangerouslySetInnerHTML={{ __html: answer }} />}
      {isOpen && !answer && <div className="answer-loading"><span />正在加载完整答案…</div>}
      <footer className="question-footer">
        <label>
          <input type="checkbox" checked={isMastered} onChange={onToggleMastered} />
          <span>{isMastered ? "已掌握" : "标记为已掌握"}</span>
        </label>
        <button type="button" onClick={onCopy}>{copied ? "已复制 ✓" : "复制链接 #"}</button>
      </footer>
    </article>
  );
}

export default function HandbookApp() {
  const [handbookId, setHandbookId] = useState(handbooks[0].id);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const [mastered, setMastered] = useState<Set<string>>(new Set());
  const [openQuestions, setOpenQuestions] = useState<Set<string>>(new Set());
  const [activeSection, setActiveSection] = useState(handbooks[0].sections[0].id);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [libraryOpen, setLibraryOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [answerChunks, setAnswerChunks] = useState<Record<string, Record<string, string>>>({});
  const searchRef = useRef<HTMLInputElement>(null);
  const chunkPromises = useRef(new Map<string, Promise<Record<string, string>>>());

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
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "/" && document.activeElement !== searchRef.current) {
        event.preventDefault();
        searchRef.current?.focus();
      }
      if (event.key === "Escape") {
        setMobileNavOpen(false);
        setLibraryOpen(false);
        searchRef.current?.blur();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    const nodes = [...document.querySelectorAll<HTMLElement>("[data-handbook-section]")];
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.find((entry) => entry.isIntersecting);
      if (visible) setActiveSection((visible.target as HTMLElement).dataset.handbookSection ?? handbook.sections[0].id);
    }, { rootMargin: "-18% 0px -70% 0px" });
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, [handbook, query, filter]);

  useEffect(() => {
    const questionId = decodeURIComponent(location.hash.slice(1));
    const question = handbook.sections.flatMap((section) => section.questions).find((candidate) => candidate.id === questionId);
    if (!questionId || !question) return;
    let request = chunkPromises.current.get(question.answerPath);
    if (!request) {
      request = fetch(question.answerPath).then((response) => response.json() as Promise<Record<string, string>>);
      chunkPromises.current.set(question.answerPath, request);
    }
    void request.then((chunk) => setAnswerChunks((current) => ({ ...current, [question.answerPath]: chunk })));
    const timer = window.setTimeout(() => {
      setOpenQuestions((current) => new Set(current).add(questionId));
      document.getElementById(questionId)?.scrollIntoView({ block: "start" });
    }, 100);
    return () => window.clearTimeout(timer);
  }, [handbook]);

  const normalizedQuery = query.trim().toLocaleLowerCase();
  const visibleSections = useMemo(() => handbook.sections.map((section) => ({
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
  })).filter((section) => section.questions.length > 0), [filter, handbook, mastered, normalizedQuery]);

  const visibleQuestions = visibleSections.flatMap((section) => section.questions);
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

  const goToQuestion = (questionId: string) => {
    const question = handbook.sections.flatMap((section) => section.questions).find((candidate) => candidate.id === questionId);
    if (question) void loadAnswer(question);
    setOpenQuestions((current) => new Set(current).add(questionId));
    history.replaceState(null, "", `#${questionId}`);
    window.setTimeout(() => document.getElementById(questionId)?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
  };

  const copyQuestionLink = async (questionId: string) => {
    const url = `${location.href.split("#")[0]}#${questionId}`;
    history.replaceState(null, "", `#${questionId}`);
    try { await navigator.clipboard.writeText(url); } catch { /* Hash still provides a usable fallback. */ }
    setCopiedId(questionId);
    window.setTimeout(() => setCopiedId(null), 1100);
  };

  const randomQuestion = () => {
    const pool = visibleQuestions.length ? visibleQuestions : handbook.sections.flatMap((section) => section.questions);
    const randomValue = window.crypto.getRandomValues(new Uint32Array(1))[0] / 2 ** 32;
    goToQuestion(pool[Math.floor(randomValue * pool.length)].id);
  };

  const switchHandbook = (nextId: string) => {
    const next = handbooks.find((candidate) => candidate.id === nextId);
    if (!next) return;
    setHandbookId(nextId);
    setQuery("");
    setFilter("all");
    setOpenQuestions(new Set());
    setActiveSection(next.sections[0].id);
    setLibraryOpen(false);
    history.replaceState(null, "", location.pathname);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const toggleTheme = () => {
    setDarkMode((current) => {
      const next = !current;
      document.documentElement.dataset.theme = next ? "dark" : "light";
      localStorage.setItem(THEME_KEY, next ? "dark" : "light");
      return next;
    });
  };

  return (
    <main className="app-shell">
      <aside className={`rail${mobileNavOpen ? " mobile-open" : ""}`}>
        <div className="rail-head">
          <a className="wordmark" href="#top" onClick={() => setMobileNavOpen(false)}>
            <span className="wordmark-mark">IA</span><span>Interview Atlas</span>
          </a>
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
            <a className={activeSection === section.id ? "module-link active" : "module-link"} href={`#section-${section.id}`} key={section.id} onClick={() => { setActiveSection(section.id); setMobileNavOpen(false); }}>
              <span className="module-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="module-name">{section.title.replace(/^\d+\s*·\s*/, "")}</span>
              <span className="module-count">{section.questions.length}</span>
            </a>
          ))}
        </nav>
        <a className="add-content" href="#content-guide" onClick={() => setMobileNavOpen(false)}><span>+</span> 以后怎么加资料</a>
        <div className="rail-progress">
          <div><span>复习进度</span><b>{masteredCount} / {handbook.stats.questions}</b></div>
          <div className="progress-track"><span style={{ width: `${progress}%` }} /></div>
          <p>{masteredCount ? `已经掌握 ${Math.round(progress)}%，继续保持。` : "每掌握一题，这里就会向前一点。"}</p>
        </div>
      </aside>
      {mobileNavOpen && <button className="nav-backdrop" type="button" onClick={() => setMobileNavOpen(false)} aria-label="关闭导航" />}

      <section className="workspace" id="top">
        <header className="topbar">
          <button className="mobile-menu" type="button" onClick={() => setMobileNavOpen(true)} aria-label="打开导航">☰</button>
          <label className="search-field">
            <span aria-hidden="true">⌕</span>
            <input ref={searchRef} value={query} onChange={(event) => setQuery(event.target.value)} type="search" placeholder="搜索 DPO、Skill、ZeRO 或某家公司…" aria-label="搜索手册" />
            {query ? <button type="button" onClick={() => setQuery("")} aria-label="清除搜索">×</button> : <kbd>/</kbd>}
          </label>
          <span className="result-count">{visibleQuestions.length} / {handbook.stats.questions} 题</span>
          <button className="icon-button" type="button" onClick={toggleTheme} aria-label="切换主题">{darkMode ? "☀" : "◐"}</button>
        </header>

        <div className="page-wrap">
          <section className="hero">
            <div className="hero-copy">
              <div className="eyebrow"><span /> {handbook.edition} · INTERVIEW HANDBOOK</div>
              <h1>把知识点，<br />变成你的<span>面试反射</span>。</h1>
              <p>{handbook.description}</p>
              <div className="audience-line">{handbook.audience}</div>
              <div className="hero-actions">
                <a href={`#section-${handbook.sections[0].id}`} className="primary-action">继续复习 <span>→</span></a>
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
          </section>

          <section className="study-controls" aria-label="复习筛选">
            <div className="filter-row">
              {([
                ["all", "全部"], ["S", "S 级"], ["A", "A 级"], ["real", "真实面经"], ["mastered", "已掌握"], ["unmastered", "未掌握"],
              ] as [Filter, string][]).map(([value, label]) => <button className={filter === value ? "active" : ""} type="button" key={value} onClick={() => setFilter(value)}>{label}</button>)}
            </div>
            <div className="bulk-actions">
              <button type="button" onClick={() => { visibleQuestions.forEach((question) => void loadAnswer(question)); setOpenQuestions(new Set(visibleQuestions.map((question) => question.id))); }}>全部展开</button>
              <button type="button" onClick={() => setOpenQuestions(new Set())}>全部折叠</button>
            </div>
          </section>

          <div className="question-sections">
            {visibleSections.map((section) => (
              <section className="question-section" id={`section-${section.id}`} data-handbook-section={section.id} key={section.id}>
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
                      copied={copiedId === question.id}
                      answer={answerChunks[question.answerPath]?.[question.id]}
                      onToggleOpen={() => toggleOpen(question)}
                      onToggleMastered={() => toggleMastered(question.id)}
                      onCopy={() => copyQuestionLink(question.id)}
                    />
                  ))}
                </div>
              </section>
            ))}
            {visibleSections.length === 0 && <div className="empty-state"><b>没有找到匹配的题目</b><p>试试换一个关键词，或清除当前筛选。</p><button type="button" onClick={() => { setQuery(""); setFilter("all"); }}>清除条件</button></div>}
          </div>

          <section className="content-guide" id="content-guide">
            <div className="guide-number">+N</div>
            <div><div className="eyebrow"><span /> CONTENT FIRST</div><h2>新资料只需要进内容层。</h2></div>
            <p>页面、搜索、筛选、复习进度都由通用组件负责。以后每新增一题，只需要放入一个独立 Markdown 文件；构建器会自动汇总、校验并生成资料库。</p>
            <a href="#top">回到顶部 ↑</a>
          </section>
        </div>
      </section>
    </main>
  );
}
