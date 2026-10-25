"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { PythonEditor } from "./PythonEditor";
import { PracticeDescription } from "./PracticeDescription";

type ExampleCase = { name: string; input: string; output: string; origin: string };
type Exercise = {
  id: string; book: string; starter: string; reference: string; tests: string; note: string;
  description: string; constraints: string[]; examples: ExampleCase[];
  source: { label: string; url: string | null; kind: string; retrievedAt?: string };
  language?: "python" | "javascript";
  legacyTests?: string;
};
type Health = { python: string; device: string; packages: Record<string, string | null> };
type RunResult = {
  status: string; stdout: string; stderr: string; durationMs: number; exitCode: number;
  checks: { line: number; label: string; passed: boolean }[]; plots: string[];
  error: { type: string; message: string; file: string | null; line: number | null; traceback: string } | null;
};

const EXAMPLES: Record<string, Exercise & { title: string }> = {
  torch: {
    id: "demo-torch", book: "examples", title: "PyTorch · 张量与自动求导", note: "CPU 小例子：修改张量或运算，观察梯度与断言结果。",
    description: "给定需要求导的张量 `x = [1, 2, 3]`，计算所有元素平方的和，执行反向传播，并检查 `x.grad`。预期损失为 14，各位置的梯度为对应输入的两倍。",
    constraints: ["使用 CPU 和浮点张量；x.requires_grad=True。"], examples: [{ name: "默认测例 1", input: "x = [1, 2, 3]", output: "loss = 14; gradient = [2, 4, 6]", origin: "handbook" }], source: { label: "手册自定义练习", url: null, kind: "handbook" },
    starter: 'import torch\n\nx = torch.tensor([1., 2., 3.], requires_grad=True)\nloss = (x ** 2).sum()\nloss.backward()\nprint("loss:", loss.item())\nprint("gradient:", x.grad)\n',
    reference: '', tests: 'assert loss.item() == 14\ntorch.testing.assert_close(x.grad, torch.tensor([2., 4., 6.]))\n',
  },
  data: {
    id: "demo-data", book: "examples", title: "数据科学 · 聚合与绘图", note: "pandas 聚合、scikit-learn 拟合和 Matplotlib 绘图；图片出现在运行结果中。",
    description: "给定三行数据：`x=[1,2,3]`、`y=[3,5,7]`。用 pandas 创建表格，用线性回归拟合 x 与 y 的关系，预测 x=4 的值，再画出已有数据点。",
    constraints: ["使用 pandas、scikit-learn 和 Matplotlib。", "浮点预测值使用带容差的断言检查。"], examples: [{ name: "默认测例 1", input: "x = [1, 2, 3], y = [3, 5, 7]; query = 4", output: "prediction = 9；生成一张数据图", origin: "handbook" }], source: { label: "手册自定义练习", url: null, kind: "handbook" },
    starter: 'import pandas as pd\nimport matplotlib.pyplot as plt\nfrom sklearn.linear_model import LinearRegression\n\ndf = pd.DataFrame({"x": [1, 2, 3], "y": [3, 5, 7]})\nmodel = LinearRegression().fit(df[["x"]], df["y"])\nprint(df.describe())\nprint("prediction:", model.predict([[4]]))\nplt.plot(df["x"], df["y"], "o-")\nplt.title("Small data example")\n',
    reference: '', tests: 'import numpy as np\nnp.testing.assert_allclose(model.predict(pd.DataFrame({"x": [4]})), [9.])\nassert len(df) == 3\n',
  },
  algorithm: {
    id: "demo-algorithm", book: "examples", title: "算法 · 两数之和", note: "实现 two_sum；先运行测试观察失败，再补上哈希表解法。",
    description: "实现 `two_sum(nums, target)`：找出数组中两个不同位置，使对应元素之和等于 target，返回这两个位置的下标。默认测试使用的输入都恰好有一组解。",
    constraints: ["同一个位置不能使用两次。"], examples: [{ name: "默认测例 1", input: "nums = [2, 7, 11, 15], target = 9", output: "[0, 1]", origin: "handbook" }, { name: "默认测例 2", input: "nums = [3, 3], target = 6", output: "[0, 1]", origin: "handbook" }], source: { label: "手册自定义练习", url: null, kind: "handbook" },
    starter: 'def two_sum(nums, target):\n    # 返回两个不同位置的下标\n    raise NotImplementedError\n',
    reference: 'def two_sum(nums, target):\n    seen = {}\n    for i, value in enumerate(nums):\n        if target - value in seen:\n            return [seen[target - value], i]\n        seen[value] = i\n    return []\n',
    tests: 'assert two_sum([2, 7, 11, 15], 9) == [0, 1]\nassert two_sum([3, 3], 6) == [0, 1]\nassert two_sum([-1, 0, 1], 0) == [0, 2]\n',
  },
};
for (const example of Object.values(EXAMPLES)) if (!example.reference) example.reference = example.starter;
const STATUS: Record<string, string> = { passed: "运行通过", failed: "运行失败", timeout: "运行超时", cancelled: "已停止", output_limit: "输出超过上限" };

async function api<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api/practice/${path}`, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({ error: "本地运行器未连接，请使用 npm run practice 启动。" }));
  if (!response.ok) throw new Error(data.error ?? "请求失败");
  return data as T;
}

export default function CodingPlayground() {
  const [exercise, setExercise] = useState<Exercise>(EXAMPLES.torch);
  const [title, setTitle] = useState(EXAMPLES.torch.title);
  const [returnHref, setReturnHref] = useState("/");
  const [code, setCode] = useState(EXAMPLES.torch.starter);
  const [tests, setTests] = useState(EXAMPLES.torch.tests);
  const [stdin, setStdin] = useState("");
  const [tab, setTab] = useState<"tests" | "stdin">("tests");
  const [truthOpen, setTruthOpen] = useState(false);
  const [resultMode, setResultMode] = useState<"solution" | "ground-truth">("solution");
  const [health, setHealth] = useState<Health | null>(null);
  const [connectionError, setConnectionError] = useState("");
  const [notice, setNotice] = useState("");
  const [ready, setReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [runError, setRunError] = useState("");
  const [timeout, setTimeoutSeconds] = useState(15);
  const [focus, setFocus] = useState<{ file: string; line: number } | null>(null);
  const currentRun = useRef<string | null>(null);
  const alive = useRef(true);
  const draftKey = `handbook-practice:v1:${exercise.book}:${exercise.id}`;

  const installExercise = useCallback((next: Exercise, nextTitle: string) => {
    let draft: { code?: string; tests?: string; stdin?: string } = {};
    try { const parsed = JSON.parse(localStorage.getItem(`handbook-practice:v1:${next.book}:${next.id}`) ?? "{}"); if (parsed && typeof parsed === "object") draft = parsed; } catch { /* storage is optional */ }
    setExercise(next); setTitle(nextTitle);
    setCode(typeof draft.code === "string" ? draft.code : next.starter);
    // Upgrade untouched old defaults without replacing hand-edited tests or code.
    const savedTests = typeof draft.tests === "string" ? draft.tests : null;
    const oldDefault = savedTests !== null && next.legacyTests !== undefined && savedTests.trim() === next.legacyTests.trim();
    setTests(savedTests !== null && !oldDefault ? savedTests : next.tests);
    setStdin(typeof draft.stdin === "string" ? draft.stdin : "");
    setResult(null); setFocus(null); setRunError(""); setTab("tests"); setTruthOpen(false); setReady(true);
  }, []);

  useEffect(() => {
    alive.current = true;
    api<Health>("health").then(setHealth).catch((error) => setConnectionError(error.message));
    const query = new URLSearchParams(location.search);
    const book = query.get("book"), question = query.get("question");
    if (book && question) {
      const destination = new URLSearchParams({ book, question });
      const section = query.get("section");
      if (section) destination.set("section", section);
      setReturnHref(`/?${destination}`);
      api<Exercise>(`exercise?book=${encodeURIComponent(book)}&question=${encodeURIComponent(question)}`)
        .then((next) => { if (alive.current) installExercise(next, query.get("title") ?? (next as Exercise & { title?: string }).title ?? question); })
        .catch((error) => { if (alive.current) { setNotice(`题目载入失败：${error.message}。你仍可在下方自由练习。`); installExercise(EXAMPLES.torch, EXAMPLES.torch.title); } })
        .finally(() => { if (alive.current) setLoading(false); });
    } else void Promise.resolve().then(() => {
      if (alive.current) { installExercise(EXAMPLES.torch, EXAMPLES.torch.title); setLoading(false); }
    });
    return () => {
      alive.current = false;
      if (currentRun.current) void api("stop", { id: currentRun.current }).catch(() => {});
    };
  }, [installExercise]);

  useEffect(() => {
    if (!ready) return;
    try { localStorage.setItem(draftKey, JSON.stringify({ code, tests, stdin })); }
    catch { queueMicrotask(() => setNotice("浏览器无法保存草稿，请使用下载按钮保留代码。")); }
  }, [code, tests, stdin, draftKey, ready]);

  const run = useCallback(async (withTests: boolean, groundTruth = false) => {
    if (currentRun.current || !health) return;
    const id = crypto.randomUUID(); currentRun.current = id;
    setRunning(true); setResult(null); setRunError(""); setFocus(null); setResultMode(groundTruth ? "ground-truth" : "solution");
    try {
      const next = await api<RunResult>("run", { id, code: groundTruth ? exercise.reference : code, tests: withTests ? (groundTruth ? exercise.tests : tests) : "", stdin, timeout, language: exercise.language ?? "python" });
      if (alive.current) setResult(next);
    } catch (error) { if (alive.current) setRunError(error instanceof Error ? error.message : "运行失败"); }
    finally { currentRun.current = null; if (alive.current) setRunning(false); }
  }, [code, tests, stdin, timeout, health, exercise]);

  const stop = async () => {
    if (currentRun.current) {
      try { await api("stop", { id: currentRun.current }); }
      catch (error) { setRunError(error instanceof Error ? error.message : "停止失败"); }
    }
  };
  const goToError = (file: string, line: number) => {
    if (resultMode === "ground-truth" && file === "user_code.py") { setTruthOpen(true); setFocus({ file: "ground_truth.py", line }); return; }
    if (file === "test_code.py") setTab("tests");
    setFocus({ file, line });
  };
  const download = () => {
    const js = exercise.language === "javascript";
    const url = URL.createObjectURL(new Blob([code, js ? "\n\n// Tests\n" : "\n\n# Tests\n", tests], { type: "text/plain" }));
    const link = document.createElement("a"); link.href = url; link.download = `${exercise.id}.${js ? "mjs" : "py"}`; link.click(); URL.revokeObjectURL(url);
  };

  return (
    <main className="coding-lab">
      <header className="lab-header">
        <a className="lab-back" href={returnHref}>← 返回手册</a>
        <div className="lab-runtime">{health ? <><span className="lab-online" />{exercise.language === "javascript" ? "Node.js" : `Python ${health.python} · CPU`} · 本地运行</> : "运行器未连接"}</div>
      </header>
      <div className="lab-heading"><div><p className="lab-eyebrow">CODING PRACTICE</p><h1>{title}</h1><p>{exercise.note}</p></div>
        <label className="lab-example">试一试<select aria-label="选择练习示例" disabled={running || loading} defaultValue="" onChange={(event) => {
          const next = EXAMPLES[event.target.value]; if (next) { history.replaceState(null, "", "/practice"); setNotice(""); installExercise(next, next.title); }
        }}><option value="" disabled>切换示例</option><option value="torch">PyTorch 自动求导</option><option value="data">数据处理与绘图</option><option value="algorithm">两数之和</option></select></label>
      </div>
      {connectionError && <div className="lab-message" role="alert">{connectionError} <code>npm run practice:setup</code> 安装依赖，然后 <code>npm run practice</code> 启动。</div>}
      {notice && <div className="lab-message" role="status">{notice}</div>}
      {loading ? <p className="answer-loading">正在准备题目与测试…</p> : <>
        <div className="lab-problem-grid">
          <section className="lab-statement"><div className="lab-section-heading"><h2>题目描述</h2>{exercise.source.url && <a href={exercise.source.url} target="_blank" rel="noopener noreferrer">官方完整原题 ↗</a>}</div>
            <PracticeDescription source={exercise.description} />
            {exercise.constraints.length > 0 && <details className="lab-constraints"><summary>输入约束 · {exercise.constraints.length} 条</summary><ul>{exercise.constraints.map((constraint, index) => <li key={index}>{constraint}</li>)}</ul></details>}
            <p className="lab-provenance">{exercise.source.kind === "leetcode" ? "题意由手册整理；示例与约束来自 LeetCode 官方公开题面。" : "手册自定义接口与默认测试约定。"}</p>
          </section>
          <section className="lab-default-cases"><div className="lab-section-heading"><h2>{exercise.source.kind === "leetcode" ? "官方公开测例" : "默认测例"}</h2><span>{exercise.examples.length} 组</span></div>
            {exercise.examples.map((example, index) => <article className="lab-example-case" key={index}><h3>{example.name}</h3><dl><dt>输入 / 调用</dt><dd><pre>{example.input}</pre></dd><dt>预期输出</dt><dd><pre>{example.output}</pre></dd></dl></article>)}
            <p className="lab-provenance">{exercise.source.kind === "leetcode" ? "这些是官方公开示例，不包含平台隐藏测试。" : "涉及局部变量时，输入准备和完整操作序列见下方测试编辑器。"}</p>
          </section>
        </div>
        <div className="lab-toolbar">
          <button className="lab-primary" disabled={!health || running} onClick={() => void run(true)}>{running ? "运行中…" : "运行测试"}</button>
          <button disabled={!health || running} onClick={() => void run(false)}>仅运行代码</button>
          <button disabled={!running} onClick={() => void stop()}>停止</button>
          <span className="lab-shortcut">⌘ / Ctrl + Enter 运行测试</span>
          <label className="lab-timeout">超时<select aria-label="运行超时" value={timeout} disabled={running} onChange={(event) => setTimeoutSeconds(Number(event.target.value))}><option value={5}>5 秒</option><option value={15}>15 秒</option><option value={30}>30 秒</option></select></label>
          <button onClick={download}>下载代码</button>
        </div>
        <div className="lab-editors">
          <section className="lab-pane"><div className="lab-pane-heading"><h2>我的代码 <span>{exercise.language === "javascript" ? "user_code.mjs" : "user_code.py"}</span></h2><span className="lab-autosave">草稿自动保存于本机</span></div>
            <PythonEditor label="我的代码" value={code} onChange={setCode} language={exercise.language} focusLine={focus?.file === "user_code.py" ? focus.line : undefined} onRun={() => void run(true)} />
          </section>
          <section className="lab-pane"><div className="lab-test-heading"><div className="lab-tabs" role="tablist" aria-label="测试与输入"><button role="tab" aria-selected={tab === "tests"} onClick={() => setTab("tests")}>测试用例</button><button role="tab" aria-selected={tab === "stdin"} onClick={() => setTab("stdin")}>标准输入</button></div><button className="lab-restore-tests" disabled={running || tests === exercise.tests} onClick={() => setTests(exercise.tests)}>恢复默认测例</button></div>
            {tab === "tests" && <PythonEditor label="测试用例代码" value={tests} onChange={setTests} language={exercise.language} focusLine={focus?.file === "test_code.py" ? focus.line : undefined} onRun={() => void run(true)} />}
            {tab === "stdin" && <label className="lab-stdin">提供给 input() 或 sys.stdin 的内容<textarea aria-label="标准输入内容" value={stdin} onChange={(event) => setStdin(event.target.value)} placeholder="每行输入一组数据…" /></label>}
          </section>
        </div>
        <section className="lab-results" aria-live="polite"><div className="lab-result-heading"><h2>{resultMode === "ground-truth" ? "Ground truth 验证结果" : "运行结果"}</h2>{result && <span className={`lab-status ${result.status}`}>{STATUS[result.status] ?? result.status} · {(result.durationMs / 1000).toFixed(2)} 秒</span>}</div>
          {!running && !result && !runError && <p className="lab-empty">运行后在这里查看输出、断言结果和错误位置。</p>}
          {running && <p className="lab-empty">正在执行，最多等待 {timeout} 秒。可以随时停止。</p>}
          {runError && <p className="lab-error" role="alert">{runError}</p>}
          {result && <>
            {result.checks.length > 0 && <ul className="lab-checks">{result.checks.map((check, index) => <li key={index} className={check.passed ? "passed" : "failed"}><button onClick={() => goToError("test_code.py", check.line)}>{check.passed ? "✓" : "✕"} 测试第 {check.line} 行</button><code>{check.label}</code></li>)}</ul>}
            {result.error && <div className="lab-error"><strong>{result.error.type}: {result.error.message || "检查未通过"}</strong>{result.error.file && result.error.line && <button onClick={() => goToError(result.error!.file!, result.error!.line!)}>定位 {result.error.file}:{result.error.line} →</button>}<details><summary>完整报错</summary><pre>{result.error.traceback}</pre></details></div>}
            {result.stdout && <div className="lab-output"><h3>标准输出</h3><pre>{result.stdout}</pre></div>}
            {result.stderr && <div className="lab-output"><h3>诊断输出</h3><pre>{result.stderr}</pre></div>}
            {result.plots.map((plot, index) => <figure className="lab-plot" key={index}>
              {/* eslint-disable-next-line @next/next/no-img-element -- locally generated PNG artifact */}
              <img src={`data:image/png;base64,${plot}`} alt={`运行生成的图 ${index + 1}`} />
            </figure>)}
            {result.status === "timeout" && <p className="lab-error">执行超过 {timeout} 秒，已终止本次进程。检查循环是否会结束，或选择更长的超时时间。</p>}
            {result.status === "output_limit" && <p className="lab-error">输出超过上限，已停止运行。请减少循环中的打印。</p>}
            {result.status === "failed" && !result.error && <p className="lab-error">进程异常退出（退出码 {result.exitCode}），请查看诊断输出。</p>}
          </>}
        </section>
        <details className="lab-ground-truth" open={truthOpen} onToggle={(event) => setTruthOpen(event.currentTarget.open)}>
          <summary>Ground truth · 参考实现与预期结果 <span>默认隐藏，完成后再对照</span></summary>
          {truthOpen && <div className="lab-truth-content"><p>以下为手册参考实现。验证时使用本题的默认测试，不会替换你的代码或已编辑的测例。</p>
            <button className="lab-verify-truth" disabled={!health || running} onClick={() => void run(true, true)}>运行参考实现，验证默认测例</button>
            <div className="lab-truth-editor"><PythonEditor label="只读 Ground truth 参考实现" value={exercise.reference} language={exercise.language} readOnly focusLine={focus?.file === "ground_truth.py" ? focus.line : undefined} /></div>
            <h3>预期结果</h3><ul>{exercise.examples.map((example, index) => <li key={index}><strong>{example.name}</strong><pre>{example.output}</pre></li>)}</ul>
          </div>}
        </details>
      </>}
      {health && <details className="lab-packages"><summary>已安装的 Python 包</summary><div>{Object.entries(health.packages).map(([name, version]) => <code key={name}>{name} {version ?? "未安装"}</code>)}</div></details>}
    </main>
  );
}
