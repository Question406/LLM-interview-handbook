"use client";

import type { FilterId, FilterOption } from "@/lib/handbook-filters";

export function StudyControls({
  filters,
  filter,
  onFilter,
  onExpandVisible,
  onCollapseAll,
  showSolutionToggle,
  revealSolutions,
  onToggleSolutions,
}: {
  filters: FilterOption[];
  filter: FilterId;
  onFilter: (value: FilterId) => void;
  onExpandVisible: () => void;
  onCollapseAll: () => void;
  showSolutionToggle: boolean;
  revealSolutions: boolean;
  onToggleSolutions: () => void;
}) {
  return (
    <section className="study-controls" aria-label="复习筛选">
      <div className="filter-row">
        {filters.map((option) => (
          <button className={filter === option.id ? "active" : ""} type="button" key={option.id} onClick={() => onFilter(option.id)}>
            {option.label}
          </button>
        ))}
      </div>
      <div className="study-actions">
        {showSolutionToggle && (
          <button
            type="button"
            className={`solution-toggle${revealSolutions ? " active" : ""}`}
            aria-pressed={revealSolutions}
            onClick={onToggleSolutions}
            title="编程题默认隐藏参考实现，先自己写；打开后全部显示"
          >
            显示全部参考实现
          </button>
        )}
        <div className="bulk-actions">
          <button type="button" onClick={onExpandVisible}>展开可见</button>
          <button type="button" onClick={onCollapseAll}>全部折叠</button>
        </div>
      </div>
    </section>
  );
}
