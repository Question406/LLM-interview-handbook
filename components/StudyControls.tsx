"use client";

import type { FilterId, FilterOption } from "@/lib/handbook-filters";

export function StudyControls({
  filters,
  filter,
  onFilter,
  onExpandVisible,
  onCollapseAll,
}: {
  filters: FilterOption[];
  filter: FilterId;
  onFilter: (value: FilterId) => void;
  onExpandVisible: () => void;
  onCollapseAll: () => void;
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
      <div className="bulk-actions">
        <button type="button" onClick={onExpandVisible}>展开可见</button>
        <button type="button" onClick={onCollapseAll}>全部折叠</button>
      </div>
    </section>
  );
}
