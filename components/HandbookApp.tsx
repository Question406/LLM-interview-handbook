"use client";

import { useEffect, useState } from "react";
import type { Handbook, HandbookCatalogEntry } from "@/content/types";
import { sortHandbooks, validateCatalog, validateHandbook } from "@/content/validate";
import { fetchJson } from "@/lib/handbook";
import { parseHandbookSearch, resolveCatalogEntry } from "@/lib/handbook-route";
import { EmptyState } from "./ShellExtras";
import { HandbookWorkspace } from "./HandbookWorkspace";

export default function HandbookApp() {
  const [catalog, setCatalog] = useState<HandbookCatalogEntry[] | null>(null);
  const [initialHandbook, setInitialHandbook] = useState<Handbook | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchJson<HandbookCatalogEntry[]>("/content/catalog.json")
      .then((data) => {
        const nextCatalog = sortHandbooks(data.map(validateCatalog));
        const parsed = parseHandbookSearch(location.search);
        const entry = resolveCatalogEntry(nextCatalog, parsed.book) ?? nextCatalog[0];
        if (!entry) throw new Error("手册目录为空");
        return fetchJson<Handbook>(entry.indexPath).then((index) => {
          if (cancelled) return;
          setCatalog(nextCatalog);
          setInitialHandbook(validateHandbook(index));
        });
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
            <EmptyState title="手册暂时打不开" detail={loadError} />
          </div>
        </section>
      </main>
    );
  }

  if (!catalog || !initialHandbook) {
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

  return <HandbookWorkspace catalog={catalog} initialHandbook={initialHandbook} />;
}
