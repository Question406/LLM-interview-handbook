import generatedHandbooks from "./generated/registry.json";
import type { Handbook } from "./types";
import { sortHandbooks, validateHandbook } from "./validate";

export const handbooks: Handbook[] = sortHandbooks(
  (generatedHandbooks as Handbook[]).map(validateHandbook),
);
