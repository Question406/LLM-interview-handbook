import type { Handbook, HandbookQuestion, HandbookSection } from "@/content/types";

export function qualifiedId(handbookId: string, questionId: string) {
  return `${handbookId}/${questionId}`;
}

export function findQuestionInHandbook(handbook: Handbook, questionId: string): { question: HandbookQuestion; section: HandbookSection } | undefined {
  for (const section of handbook.sections) {
    const question = section.questions.find((candidate) => candidate.id === questionId);
    if (question) return { question, section };
  }
  return undefined;
}

export function isTextEntryTarget(target: EventTarget | null) {
  return target instanceof HTMLInputElement
    || target instanceof HTMLTextAreaElement
    || (target instanceof HTMLElement && target.isContentEditable);
}

export function displayPlain(text: string) {
  return text.replace(/\$\$([\s\S]+?)\$\$/g, "$1").replace(/\$([^$\n]+?)\$/g, "$1");
}

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}（${response.status}）`);
  return response.json() as Promise<T>;
}

export function questionPrompt(question: HandbookQuestion, sectionTitle: string) {
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

export async function writeClipboard(text: string) {
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
