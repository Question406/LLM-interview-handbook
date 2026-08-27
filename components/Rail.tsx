"use client";

import type { Handbook, HandbookCatalogEntry } from "@/content/types";

export function Rail({
  handbook,
  catalog,
  activeSection,
  isSearching,
  masteredCount,
  progress,
  libraryOpen,
  mobileNavOpen,
  onOverview,
  onToggleLibrary,
  onSwitchHandbook,
  onOpenSection,
  onOpenGuide,
  onCloseMobile,
}: {
  handbook: Handbook;
  catalog: HandbookCatalogEntry[];
  activeSection: string | null;
  isSearching: boolean;
  masteredCount: number;
  progress: number;
  libraryOpen: boolean;
  mobileNavOpen: boolean;
  onOverview: () => void;
  onToggleLibrary: () => void;
  onSwitchHandbook: (id: string) => void;
  onOpenSection: (sectionId: string) => void;
  onOpenGuide: () => void;
  onCloseMobile: () => void;
}) {
  return (
    <aside className={`rail${mobileNavOpen ? " mobile-open" : ""}`}>
      <div className="rail-head">
        <button className="wordmark" type="button" onClick={onOverview}>
          <span className="wordmark-mark">面</span><span>面试题库</span>
        </button>
        <button className="mobile-close" type="button" onClick={onCloseMobile} aria-label="关闭导航">×</button>
      </div>

      <div className="library-switcher">
        <button type="button" onClick={onToggleLibrary} aria-expanded={libraryOpen}>
          <span><small>当前资料</small><b>{handbook.shortTitle}</b></span><span>{libraryOpen ? "−" : "+"}</span>
        </button>
        {libraryOpen && <div className="library-menu">
          {catalog.map((candidate) => (
            <button type="button" className={candidate.id === handbook.id ? "active" : ""} key={candidate.id} onClick={() => onSwitchHandbook(candidate.id)}>
              <span>{candidate.shortTitle}</span><small>{candidate.stats.questions} 题</small>
            </button>
          ))}
        </div>}
      </div>

      <div className="rail-label">手册目录</div>
      <nav className="module-nav" aria-label="手册目录">
        {handbook.sections.map((section, index) => (
          <button className={activeSection === section.id && !isSearching ? "module-link active" : "module-link"} type="button" key={section.id} onClick={() => onOpenSection(section.id)}>
            <span className="module-index">{String(index + 1).padStart(2, "0")}</span>
            <span className="module-name">{section.title.replace(/^\d+\s*·\s*/, "")}</span>
            <span className="module-count">{section.questions.length}</span>
          </button>
        ))}
      </nav>
      <button className="add-content" type="button" onClick={onOpenGuide}><span>+</span> 以后怎么加资料</button>
      <div className="rail-progress">
        <div><span>复习进度</span><b>{masteredCount} / {handbook.stats.questions}</b></div>
        <div className="progress-track"><span style={{ width: `${progress}%` }} /></div>
        <p>{masteredCount ? `已经掌握 ${Math.round(progress)}%，继续保持。` : "每掌握一题，这里就会向前一点。"}</p>
      </div>
    </aside>
  );
}
