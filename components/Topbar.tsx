"use client";

import type { RefObject } from "react";

export function Topbar({
  query,
  resultLabel,
  darkMode,
  searchRef,
  onQueryChange,
  onClearQuery,
  onOpenMobile,
  onOpenShortcuts,
  onToggleTheme,
}: {
  query: string;
  resultLabel: string;
  darkMode: boolean;
  searchRef: RefObject<HTMLInputElement | null>;
  onQueryChange: (value: string) => void;
  onClearQuery: () => void;
  onOpenMobile: () => void;
  onOpenShortcuts: () => void;
  onToggleTheme: () => void;
}) {
  return (
    <header className="topbar">
      <button className="mobile-menu" type="button" onClick={onOpenMobile} aria-label="打开导航">☰</button>
      <label className="search-field">
        <span aria-hidden="true">⌕</span>
        <input ref={searchRef} value={query} onChange={(event) => onQueryChange(event.target.value)} type="search" placeholder="搜索 DPO、Skill、ZeRO 或某家公司…" aria-label="搜索手册" />
        {query && <button type="button" onClick={onClearQuery} aria-label="清除搜索">×</button>}
      </label>
      <span className="result-count">{resultLabel}</span>
      <button className="icon-button shortcut-button" type="button" onClick={onOpenShortcuts} aria-label="查看键盘快捷键">?</button>
      <button className="icon-button" type="button" onClick={onToggleTheme} aria-label="切换主题">{darkMode ? "☀" : "◐"}</button>
    </header>
  );
}
