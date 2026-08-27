"use client";

import { useEffect, useState } from "react";
import { qualifiedId } from "@/lib/handbook";

const STORAGE_KEY = "interview-atlas-mastered-v1";
const THEME_KEY = "interview-atlas-theme";

export function useMastered() {
  const [mastered, setMastered] = useState<Set<string>>(new Set());

  useEffect(() => {
    const timer = window.setTimeout(() => {
      try {
        const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
        setMastered(new Set(Array.isArray(stored) ? stored : []));
      } catch {
        setMastered(new Set());
      }
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const toggleMastered = (handbookId: string, questionId: string) => {
    const key = qualifiedId(handbookId, questionId);
    setMastered((current) => {
      const next = new Set(current);
      if (next.has(key)) next.delete(key); else next.add(key);
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...next]));
      return next;
    });
  };

  return { mastered, toggleMastered };
}

export function useThemePreference() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const savedTheme = localStorage.getItem(THEME_KEY);
      const shouldUseDark = savedTheme === "dark" || (!savedTheme && matchMedia("(prefers-color-scheme: dark)").matches);
      setDarkMode(shouldUseDark);
      document.documentElement.dataset.theme = shouldUseDark ? "dark" : "light";
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const toggleTheme = () => {
    setDarkMode((current) => {
      const next = !current;
      document.documentElement.dataset.theme = next ? "dark" : "light";
      localStorage.setItem(THEME_KEY, next ? "dark" : "light");
      return next;
    });
  };

  return { darkMode, toggleTheme };
}
