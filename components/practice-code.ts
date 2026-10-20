// Client-side study aids for coding-practice answers. The compiled answer HTML stays untouched
// (the rendered-code checkers compare its <pre><code> text with the markdown); we only hide,
// wrap, and annotate the existing nodes after React mounts them.

const PRACTICE_HEADING = "完整编程练习";
const IMPL_HEADING = "完整参考实现";
const TEST_HEADING = "可执行测试";

/** Per-card "show/hide reference implementation" choices that override the global toggle. */
const implOverrides = new Map<string, boolean>();
const openTests = new Set<string>();

export function resetPracticeReveals() {
  implOverrides.clear();
}

type PracticeBlocks = { impl: HTMLPreElement | null; tests: HTMLPreElement | null };

function firstPreAfter(heading: Element): HTMLPreElement | null {
  for (let el = heading.nextElementSibling; el; el = el.nextElementSibling) {
    if (el.tagName === "H2" || el.tagName === "H3") return null;
    if (el instanceof HTMLPreElement) return el;
  }
  return null;
}

function findPracticeBlocks(root: HTMLElement): PracticeBlocks {
  const blocks: PracticeBlocks = { impl: null, tests: null };
  const practice = Array.from(root.querySelectorAll("h2")).find((h2) => h2.textContent?.trim().startsWith(PRACTICE_HEADING));
  if (!practice) return blocks;
  for (let el = practice.nextElementSibling; el && el.tagName !== "H2"; el = el.nextElementSibling) {
    if (el.tagName !== "H3") continue;
    const title = el.textContent?.trim() ?? "";
    if (!blocks.impl && title.startsWith(IMPL_HEADING)) blocks.impl = firstPreAfter(el);
    else if (!blocks.tests && title.startsWith(TEST_HEADING)) blocks.tests = firstPreAfter(el);
  }
  return blocks;
}

function codeText(pre: HTMLPreElement) {
  return (pre.querySelector("code") ?? pre).textContent ?? "";
}

function lineCount(pre: HTMLPreElement) {
  return codeText(pre).replace(/\s+$/, "").split("\n").length;
}

function domId(prefix: string, questionId: string) {
  return `${prefix}-${questionId.replace(/[^A-Za-z0-9_-]/g, "_")}`;
}

function button(action: string, label: string, className: string) {
  const el = document.createElement("button");
  el.type = "button";
  el.className = className;
  el.dataset.practiceAction = action;
  el.textContent = label;
  return el;
}

/** Inserts the reveal bar, copy button, and collapsible tests. Safe to call repeatedly. */
export function enhancePractice(root: HTMLElement, questionId: string) {
  if (root.querySelector(".practice-bar")) return;
  const { impl, tests } = findPracticeBlocks(root);
  if (!impl) return;

  impl.id = domId("practice-impl", questionId);
  impl.classList.add("practice-impl");

  const bar = document.createElement("div");
  bar.className = "practice-bar";
  const hint = document.createElement("p");
  hint.className = "practice-hint";
  hint.textContent = `先自己写一遍，再对照参考实现（${lineCount(impl)} 行）。`;
  const actions = document.createElement("div");
  actions.className = "practice-actions";
  const reveal = button("reveal", "显示参考实现", "practice-btn practice-reveal");
  reveal.setAttribute("aria-controls", impl.id);
  const copy = button("copy", "复制可运行文件", "practice-btn practice-copy");
  const copyLabel = tests ? "复制参考实现与测试，合成一个可运行文件" : "复制参考实现";
  copy.setAttribute("aria-label", copyLabel);
  copy.title = copyLabel;
  actions.append(reveal, copy);
  bar.append(hint, actions);
  impl.before(bar);

  if (tests) {
    const details = document.createElement("details");
    details.className = "practice-tests";
    details.open = openTests.has(questionId);
    const summary = document.createElement("summary");
    summary.textContent = `测试代码 · ${lineCount(tests)} 行`;
    tests.classList.add("practice-test-code");
    tests.before(details);
    details.append(summary, tests);
  }
}

export function applyPracticeReveal(root: HTMLElement, questionId: string, revealAll: boolean) {
  const impl = root.querySelector<HTMLPreElement>("pre.practice-impl");
  const reveal = root.querySelector<HTMLButtonElement>(".practice-reveal");
  if (!impl || !reveal) return;
  const shown = implOverrides.get(questionId) ?? revealAll;
  impl.hidden = !shown;
  reveal.setAttribute("aria-expanded", String(shown));
  reveal.textContent = shown ? "隐藏参考实现" : "显示参考实现";
  reveal.closest(".practice-bar")?.classList.toggle("revealed", shown);
}

export function rememberTestsToggle(details: HTMLDetailsElement, questionId: string) {
  if (!details.classList.contains("practice-tests")) return false;
  if (details.open) openTests.add(questionId);
  else openTests.delete(questionId);
  return true;
}

export function runnableFile(root: HTMLElement) {
  // Read the nodes enhancePractice marked: the tests <pre> now lives inside its <details>.
  const impl = root.querySelector<HTMLPreElement>("pre.practice-impl");
  const tests = root.querySelector<HTMLPreElement>("pre.practice-test-code");
  if (!impl) return null;
  const parts = [impl, tests].filter((pre): pre is HTMLPreElement => pre !== null).map((pre) => codeText(pre).replace(/\s+$/, ""));
  return `${parts.join("\n\n\n")}\n`;
}

/** Handles clicks on the injected controls. Returns true when the click was one of ours. */
export function handlePracticeClick(
  target: Element,
  root: HTMLElement,
  questionId: string,
  revealAll: boolean,
  copy: (text: string) => Promise<void>,
) {
  const control = target.closest<HTMLButtonElement>("button[data-practice-action]");
  if (!control || !root.contains(control)) return false;
  if (control.dataset.practiceAction === "reveal") {
    const shown = control.getAttribute("aria-expanded") === "true";
    implOverrides.set(questionId, !shown);
    applyPracticeReveal(root, questionId, revealAll);
    return true;
  }
  const text = runnableFile(root);
  if (text === null) return true;
  void copy(text).then(() => {
    control.classList.add("copied");
    control.textContent = "已复制";
    window.setTimeout(() => {
      control.classList.remove("copied");
      control.textContent = "复制可运行文件";
    }, 1100);
  });
  return true;
}
