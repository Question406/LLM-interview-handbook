---
id: drustz-a5df8099ce3cadf189
section: labs
order: 19
level: A
title: swe_data · SWE agent 训练数据 pipeline（可跑）
quick: 作者完整文档 · swe_data · SWE agent 训练数据 pipeline（可跑）
companies: []
tags:
  - DrustZ
  - 作者完整文档
  - Labs · Code、Tests 与 Data
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/swe_data/README.md
    type: primary
---
# swe_data · SWE agent 训练数据 pipeline（可跑）

配套文章：[`../../21_swe_agent_data.md`](?book=drustz-interview-2026&section=mlsd&question=drustz-2f6e575475ae73e26e)

```bash
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyrepo.py                    # 造玩具仓库（9 个 commit，真 git 历史）
$V github.py                     # 仓库筛选打分 + issue 链接解析
$V mine.py                       # 挖候选 + 真跑 pytest 做 F2P/P2P 三步验证
$V synth.py                      # SWE-smith 式 AST 造 bug + 执行验证
$V curate.py                     # 去重 / 去污染 / 难度分层（跑完整条链）
$V -m pytest test_swe_data.py -q # 26 passed（约 30 秒）
```



**无网络、无 Docker、无 API key。F2P/P2P 是真跑测试跑出来的，不是模拟。**

| 文件 | 干什么 | 对应文章 |
|---|---|---|
| `toyrepo.py` | 造一个带真实 git 历史的仓库：5 个合格候选 + 3 个该被过滤 | §3 |
| `github.py` | 仓库筛选阈值（SWE-smith / SWE-rebench V2 的实际数字）+ issue 链接正则 | §2 |
| `mine.py` | PR→实例：劈 patch、便宜过滤、**三步执行验证** | §3, §5 |
| `synth.py` | 环境优先造 bug：6 种 AST 变换 + 执行筛选 | §6 |
| `curate.py` | MinHash 近重复、三层去污染、pass@k 难度 | §7 |

## 为什么用玩具仓库而不是 clone 真仓库

1. 真仓库要装依赖、跑几分钟、要网络 —— 学 pipeline 时这些全是噪声
2. **玩具仓库里我知道正确答案**（哪 5 个 commit 该被挖出来），所以能写断言
3. 它刻意埋了三种「不合格」commit：只改文档 / 只改测试 / 改代码但没加测试

`toyrepo.EXPECTED_VALID = 5` 就是 ground truth。**没有 ground truth 的 pipeline 没法调试。**

## 跑出来长什么样

```text
挖到 8 个 commit（不含 initial）
  便宜过滤后剩 5 个进入执行验证
  ✅ 0f2d65e fix: mean() crashes with ZeroDivisionError    F2P=1 P2P=1
  ...
  ❌ 63ff97d chore: clarify mean() docstring   没有测试改动 → 无法自动验证
最终 5 个可用实例（产出率 62%）

基线：7 个测试全过
尝试 24 次变异 → 7 个有效 bug（产出率 29%）

近重复去除：丢 4 条   去污染：丢 1 条   最终：7 条
```



## 三个测试专门守着容易踩的坑

- `test_solution_patch_never_touches_test_files` —— gold patch 混进测试文件 = 答案泄漏
- `test_anchored_regex_beats_the_papers_substring_match` —— 论文那条无锚定正则会把
  `contest.py` 判成测试文件
- `test_empty_normalization_raises_instead_of_silently_deduping` —— schema 不一致
  会让去重静默把所有实例判成重复（我这次真踩了）

## curate.py

```python
"""挖出来之后：**去重 → 去污染 → 难度分层 → 配比**。

这一步是 math/STEM 数据 curation 的经验**直接可以迁移**的部分，
但有三个 SWE 特有的坑：

  1. **去重的单位不是文本，是「改动的语义」。** 同一个仓库里
     「给 N 个函数各加一个 None 检查」的 PR 可能有几十个，patch 文本高度相似 ——
     它们对模型是同一道题。要在 patch 的归一化形式上做近重复检测。
  2. **去污染要按仓库 + 时间双维度。** 只查 instance_id 不够：
     SWE-bench 的 12 个测试仓库**整个仓库**都要排除（SWE-smith 就是这么做的），
     因为同一个仓库的其他 PR 会泄漏代码库结构和风格。
  3. **难度必须用「当前模型的可解率」来定，不是用 patch 行数。**
     行数只是一个 proxy，而且和难度的相关性没你以为的高。

    python curate.py
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path


# ─────────────────────────────────────────── 归一化 + 近重复
def normalize_patch(patch: str) -> str:
    """只保留**增删的代码行**，去掉 hunk 头、行号、路径、空白和注释。
    目的：让「同一种改动作用在不同文件上」被认成近重复。"""
    lines = []
    for ln in patch.splitlines():
        if ln.startswith(("+++", "---", "diff ", "index ", "@@")):
            continue
        if ln[:1] not in "+-":
            continue
        body = ln[1:].strip()
        body = re.sub(r"#.*$", "", body)  # 去注释
        body = re.sub(r"\s+", " ", body).strip()
        if body:
            lines.append(body)
    return "\n".join(lines)


def assert_is_diff(patch: str, who: str = ""):
    """**护栏**：归一化后为空 = 这不是 diff，或者 schema 变了。
    没有这一行，dedup 会把所有实例判成重复而且一声不吭。"""
    if not normalize_patch(patch).strip():
        raise ValueError(f"归一化后为空，{who} 传进来的多半不是 unified diff")


def shingles(text: str, k: int = 5) -> set:
    toks = re.findall(r"[A-Za-z_]\w*|\S", text)
    return {" ".join(toks[i : i + k]) for i in range(max(1, len(toks) - k + 1))}


def minhash(s: set, n: int = 64) -> tuple:
    """n 个哈希函数各取最小值。**手写是因为要说清它在算什么** ——
    两个集合的 MinHash 签名相同位数的比例，是 Jaccard 的无偏估计。"""
    if not s:
        return tuple([0] * n)
    sig = []
    for i in range(n):
        sig.append(
            min(int(hashlib.md5(f"{i}|{x}".encode()).hexdigest()[:8], 16) for x in s)
        )
    return tuple(sig)


def jaccard_est(a: tuple, b: tuple) -> float:
    return sum(x == y for x, y in zip(a, b)) / len(a)


def dedup(instances: list, thr: float = 0.7) -> tuple:
    """贪心近重复去除。返回 (保留, 丢弃原因列表)。
    真实规模要用 LSH 分桶，不能 O(n²)。"""
    kept, sigs, dropped = [], [], []
    for inst in instances:
        raw = inst.get("patch", "") or inst.get("bug_patch", "")
        assert_is_diff(raw, inst.get("instance_id", "?"))
        sig = minhash(shingles(normalize_patch(raw)))
        dup_of = next(
            (
                kept[i]["instance_id"]
                for i, s in enumerate(sigs)
                if jaccard_est(sig, s) >= thr
            ),
            None,
        )
        if dup_of:
            dropped.append((inst["instance_id"], f"≈{dup_of}"))
        else:
            kept.append(inst)
            sigs.append(sig)
    return kept, dropped


# ─────────────────────────────────────────── 去污染
SWEBENCH_TEST_REPOS = {  # SWE-bench 的 12 个测试仓库，整仓排除
    "astropy/astropy",
    "django/django",
    "matplotlib/matplotlib",
    "mwaskom/seaborn",
    "pallets/flask",
    "psf/requests",
    "pydata/xarray",
    "pylint-dev/pylint",
    "pytest-dev/pytest",
    "scikit-learn/scikit-learn",
    "sphinx-doc/sphinx",
    "sympy/sympy",
}


def decontaminate(
    instances: list, bench_repos=SWEBENCH_TEST_REPOS, bench_patches: list = None
) -> tuple:
    """三层：① 整仓排除 ② instance_id 精确匹配 ③ patch 近重复。

    ⚠️ **只做 ①② 是不够的**：同一个 bug 可能在 fork 里、在别的仓库的
    vendored 副本里再出现一次。③ 才能抓到。"""
    bench_sigs = [minhash(shingles(normalize_patch(p))) for p in (bench_patches or [])]
    kept, removed = [], []
    for inst in instances:
        if inst.get("repo") in bench_repos:
            removed.append((inst["instance_id"], "① 属于 benchmark 测试仓库"))
            continue
        sig = minhash(shingles(normalize_patch(inst.get("patch", ""))))
        if any(jaccard_est(sig, b) >= 0.8 for b in bench_sigs):
            removed.append((inst["instance_id"], "③ patch 与 benchmark 近重复"))
            continue
        kept.append(inst)
    return kept, removed


# ─────────────────────────────────────────── 难度
def static_difficulty(inst: dict) -> str:
    """**便宜但不可靠的 proxy。** 只用来做初筛和分桶，不能当结论。"""
    n_lines = inst.get("meta", {}).get("patch_lines", 0)
    n_files = inst.get("meta", {}).get("n_code_files", 1)
    n_f2p = len(inst.get("FAIL_TO_PASS", []))
    score = n_lines / 20 + (n_files - 1) * 1.5 + max(0, n_f2p - 1) * 0.5
    return "easy" if score < 1 else ("medium" if score < 3 else "hard")


def empirical_difficulty(inst: dict, rollout_results: list) -> dict:
    """**正确的做法**：用当前策略跑 k 次 rollout，用通过率定难度。

    这直接接你在 math/STEM 上做的自适应难度筛选 —— 同一个思路：
      * pass@k = 0   → 无梯度信号，**这一组 rollout 白跑**（GRPO 组内优势全 0）
      * pass@k = 1   → 太简单，同样无信号
      * 0 < p < 1    → 有区分度，**这才是该留的**
    """
    k = len(rollout_results)
    p = sum(rollout_results) / k if k else 0.0
    return {
        "pass_rate": p,
        "k": k,
        "keep_for_rl": 0 < p < 1,
        "bucket": "unsolvable"
        if p == 0
        else (
            "trivial"
            if p == 1
            else ("hard" if p <= 0.25 else ("medium" if p <= 0.6 else "easy"))
        ),
    }


# ─────────────────────────────────────────── 配比
def stratify(instances: list, quota: dict = None) -> list:
    """按难度桶配比。默认偏向中等难度 —— RL 的信号密度在那里最高。"""
    quota = quota or {"easy": 0.2, "medium": 0.5, "hard": 0.3}
    buckets = {}
    for i in instances:
        buckets.setdefault(static_difficulty(i), []).append(i)
    n = len(instances)
    out = []
    for b, frac in quota.items():
        out += buckets.get(b, [])[: max(1, int(n * frac))]
    return out


def report(instances: list, title: str):
    print(f"\n{title}：{len(instances)} 条")
    for k, v in Counter(static_difficulty(i) for i in instances).most_common():
        print(f"    {k:<8} {v}")


if __name__ == "__main__":
    import mine, synth, toyrepo

    root = toyrepo.build()
    mined = mine.run(root)
    synthed = synth.synthesize(root, verbose=False)
    for s in synthed:  # 统一 schema
        s["patch"] = s["bug_patch"]
        s.setdefault(
            "meta",
            {
                "patch_lines": sum(
                    1
                    for ln in s["bug_patch"].splitlines()
                    if ln[:1] in "+-" and ln[:3] not in ("+++", "---")
                ),
                "n_code_files": 1,
            },
        )
    pool = mined + synthed
    report(pool, "原始池")

    kept, dropped = dedup(pool)
    print(f"\n近重复去除：丢 {len(dropped)} 条")
    for i, why in dropped[:5]:
        print(f"    {i}  {why}")

    kept2, removed = decontaminate(
        kept, bench_patches=[mined[0]["patch"]] if mined else []
    )
    print(f"\n去污染：丢 {len(removed)} 条")
    for i, why in removed[:5]:
        print(f"    {i}  {why}")

    report(kept2, "最终")
    print("\n⚠️ static_difficulty 只是 proxy。上 RL 前必须用 empirical_difficulty")
    print("   跑一遍 rollout，把 pass@k ∈ {0, 1} 的题**先扔掉** —— 它们没有梯度。")
    demo = empirical_difficulty(kept2[0], [0, 1, 0, 0, 1, 0, 0, 0])
    print(f"   例：{kept2[0]['instance_id']} → {demo}")
```




## github.py

```python
"""从 GitHub 拿数据的三条路，以及**选仓库**的打分。

    python github.py            # 离线示例，不需要 token
    GITHUB_TOKEN=xxx python github.py --live pallets/flask

三条路，按规模和成本排序：

| 路 | 怎么拿 | 速率限制 | 适合 |
|---|---|---|---|
| **REST/GraphQL API** | `api.github.com` | 认证后 5000 req/h | 几百个仓库、要最新状态 |
| **GH Archive** | BigQuery / 下载每小时的 `.json.gz` | 无 | **全量 PR/issue 元数据**，SWE-rebench V2 用这个 |
| **本地 clone + git log** | `git clone --filter=blob:none` | 无 | 拿 patch 内容。**别用 API 逐个拉 diff** |

**SWE-rebench V2 的做法值得抄**：用 GH Archive 拿元数据（issue/PR/commit SHA/license），
然后**分布式 map-reduce 克隆仓库、从本地 git 历史取 patch**，
完全绕开 API 速率限制。他们这样处理出 21,000 个仓库 / 58 万个候选实例。
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from dataclasses import dataclass

API = "https://api.github.com"


# ─────────────────────────────────────────── 仓库筛选标准
@dataclass
class RepoFilters:
    """各家的实际阈值（可引用）：

    * **SWE-smith**：PyPI 下载量前 5000 的包 → 按 star 排序 → **剔除 <1000 star**
      → 再剔除 SWE-bench 的 12 个测试仓库。最终 128 个仓库。
    * **SWE-rebench V2**：高资源语言（Python/Java/Go）**≥25 star 且 ≥15 个 closed issue**；
      长尾语言放宽到 **≥10 star、≥1 个 closed issue**。
      他们量化过：**这个阈值保留约 20% 的仓库，却覆盖约 80% 的任务** ——
      需要做环境搭建的仓库数直接降为 1/5。这是整条 pipeline 里性价比最高的一刀。
    """

    min_stars: int = 25
    min_closed_issues: int = 15
    require_permissive_license: bool = True
    exclude_repos: frozenset = frozenset(
        {
            "astropy/astropy",
            "django/django",
            "matplotlib/matplotlib",
            "mwaskom/seaborn",
            "pallets/flask",
            "psf/requests",
            "pydata/xarray",
            "pylint-dev/pylint",
            "pytest-dev/pytest",
            "scikit-learn/scikit-learn",
            "sphinx-doc/sphinx",
            "sympy/sympy",  # SWE-bench 测试集，整仓排除
        }
    )
    languages: frozenset = frozenset({"Python"})


PERMISSIVE = {"mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause", "isc", "unlicense"}


def score_repo(meta: dict, f: RepoFilters = RepoFilters()) -> dict:
    """返回 {keep, reasons, yield_score}。

    `yield_score` 是「这个仓库大概能产出多少可用实例」的先验估计。
    **任务产出高度长尾** —— 少数核心仓库贡献大部分实例，
    所以按它排序、优先给高分仓库搭环境，是对的。
    """
    full = meta.get("full_name", "")
    reasons = []
    if full in f.exclude_repos:
        reasons.append("在 benchmark 测试集里（整仓排除）")
    if meta.get("stargazers_count", 0) < f.min_stars:
        reasons.append(f"star {meta.get('stargazers_count')} < {f.min_stars}")
    if meta.get("closed_issues", 0) < f.min_closed_issues:
        reasons.append(
            f"closed issue {meta.get('closed_issues')} < {f.min_closed_issues}"
        )
    if f.languages and meta.get("language") not in f.languages:
        reasons.append(f"语言 {meta.get('language')} 不在目标内")
    lic = (meta.get("license") or {}).get("key", "")
    if f.require_permissive_license and lic not in PERMISSIVE:
        reasons.append(f"license `{lic or 'none'}` 非宽松许可")
    if meta.get("archived"):
        reasons.append("已归档")
    if meta.get("fork"):
        reasons.append("是 fork（会和上游重复）")

    # 有测试目录 + issue 活跃 + PR 多 → 产出高
    ys = (
        min(meta.get("closed_issues", 0), 2000) / 2000 * 3
        + min(meta.get("stargazers_count", 0), 20000) / 20000 * 2
        + (2 if meta.get("has_tests") else 0)
    )
    return {
        "repo": full,
        "keep": not reasons,
        "reasons": reasons,
        "yield_score": round(ys, 2),
    }


# ─────────────────────────────────────────── 真实 API（需 token）
def _get(url: str, token: str):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "swe-data-lab",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch_repo(full_name: str, token: str) -> dict:
    m = _get(f"{API}/repos/{full_name}", token)
    # closed issue 数要单独查：repo 的 open_issues_count 含 PR，且只算 open
    s = _get(
        f"{API}/search/issues?q=repo:{full_name}+type:issue+state:closed&per_page=1",
        token,
    )
    tree = _get(f"{API}/repos/{full_name}/contents", token)
    m["closed_issues"] = s.get("total_count", 0)
    m["has_tests"] = any(e["name"] in ("tests", "test", "testing") for e in tree)
    return m


def linked_issue_numbers(pr_body: str) -> list:
    """PR 正文里 `Fixes #123` / `Closes #45` 这类引用。
    **issue 链接是 SWE-bench 系的关键**：problem_statement 用的是 issue 正文，
    不是 PR 描述 —— 因为 PR 描述常常已经把解法说出来了（**答案泄漏**）。
    拿不到 issue 时 SWE-rebench V2 才退而用 PR 描述，并单独打标记。"""
    import re

    return sorted(
        {
            int(n)
            for n in re.findall(
                r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s*:?\s*#(\d+)",
                pr_body or "",
                re.I,
            )
        }
    )


# ─────────────────────────────────────────── 离线示例
SAMPLE = [
    {
        "full_name": "pallets/flask",
        "stargazers_count": 68000,
        "closed_issues": 2600,
        "language": "Python",
        "license": {"key": "bsd-3-clause"},
        "has_tests": True,
    },
    {
        "full_name": "tqdm/tqdm",
        "stargazers_count": 29000,
        "closed_issues": 1100,
        "language": "Python",
        "license": {"key": "mit"},
        "has_tests": True,
    },
    {
        "full_name": "someone/tiny-utils",
        "stargazers_count": 12,
        "closed_issues": 3,
        "language": "Python",
        "license": {"key": "mit"},
        "has_tests": False,
    },
    {
        "full_name": "corp/internal-tool",
        "stargazers_count": 900,
        "closed_issues": 80,
        "language": "Python",
        "license": {"key": "gpl-3.0"},
        "has_tests": True,
    },
    {
        "full_name": "acme/fastapi-clone",
        "stargazers_count": 400,
        "closed_issues": 60,
        "language": "Python",
        "license": {"key": "mit"},
        "has_tests": True,
        "fork": True,
    },
    {
        "full_name": "vuejs/core",
        "stargazers_count": 47000,
        "closed_issues": 5000,
        "language": "TypeScript",
        "license": {"key": "mit"},
        "has_tests": True,
    },
]


def main():
    if "--live" in sys.argv:
        tok = os.environ.get("GITHUB_TOKEN")
        if not tok:
            sys.exit("需要 GITHUB_TOKEN")
        name = sys.argv[sys.argv.index("--live") + 1]
        meta = fetch_repo(name, tok)
        print(json.dumps(score_repo(meta), ensure_ascii=False, indent=2))
        return

    print("仓库筛选（离线示例）\n")
    rows = [score_repo(m) for m in SAMPLE]
    for r in sorted(rows, key=lambda x: -x["yield_score"]):
        tag = "✅" if r["keep"] else "❌"
        why = "" if r["keep"] else "  ← " + "；".join(r["reasons"])
        print(f"  {tag} {r['repo']:<24} yield={r['yield_score']:<5}{why}")
    kept = sum(r["keep"] for r in rows)
    print(
        f"\n保留 {kept}/{len(rows)}。**先给 yield_score 高的搭环境** —— "
        f"任务产出是长尾的，\n  SWE-rebench V2 量过：20% 的仓库覆盖 80% 的任务。"
    )

    print("\nPR 正文里的 issue 链接：")
    for body in [
        "Fixes #123 and closes #456.",
        "See #99 for context (not a fix)",
        "resolve: #7",
    ]:
        print(f"  {body!r:<42} → {linked_issue_numbers(body)}")
    print("  ⚠️ 只提到 #99 不算 —— 必须是 close/fix/resolve 这类**解决**语义。")


if __name__ == "__main__":
    main()
```




## mine.py

```python
"""从 git 历史挖 SWE 训练实例，并用**真实执行**验证 F2P / P2P。

这是 SWE-bench 家族的核心过程，一比一实现（只是把 GitHub PR 换成本地 commit，
因为 PR 的本质就是「一个 base commit + 一个 diff」）：

    候选 = 同时改了「代码文件」和「测试文件」的 commit
    solution_patch = diff 里的非测试文件部分
    test_patch     = diff 里的测试文件部分

    三步验证（缺一不可）：
      ① 在 parent commit 上跑测试         → 必须全过（证明环境是好的）
      ② 打上 test_patch 再跑              → 新测试必须 FAIL（证明 bug 真存在）
      ③ 再打上 solution_patch 跑          → 必须全过（证明这个 fix 真管用）

    F2P = ②失败 且 ③通过 的测试      ← 这是奖励信号
    P2P = ②通过 且 ③通过 的测试      ← 这是防回归的护栏

**为什么 P2P 不能省**：只用 F2P 当 reward，模型可以把不相关的代码删光
只要新测试过就行。P2P 是「别把别的东西弄坏」的约束。

    python mine.py
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path

import toyrepo
from toyrepo import sh

# SWE-rebench V2 论文里用的就是这一条（无锚定的子串匹配）
NAIVE_TEST_RE = re.compile(r"(?i)(test(?:ing|s)?|e2e)")
# 我们用的：要求**路径段边界**，避免 contest/latest 这类误判
TEST_RE = re.compile(
    r"(^|/)(tests?|testing|e2e)(/|$)|(^|/)test_[^/]*\.py$|_test\.py$", re.I
)
CODE_EXT = {".py"}
PYTEST = "/Users/mingrui/Documents/codes/interview/.venv/bin/python -m pytest"


def is_test_file(path: str) -> bool:
    """判定「这是测试文件吗」。看起来是小事，其实是 pipeline 里
    **最容易被忽略的正确性来源** —— 判错会让 gold patch 里混进测试文件（答案泄漏），
    或者把真正的测试改动漏掉（instance 被误判为「没有测试」而丢弃）。

    对比 SWE-rebench V2 论文用的 `(?i)(test(?:ing|s)?|e2e)`：
    那是**无锚定的子串匹配**，`src/contest.py`、`build/latest/x.py`
    都会被判成测试文件。我们加了路径段边界。
    （论文自己也说了要在 metadata 里标记「测试逻辑混在业务文件里」的情况。）
    """
    return bool(TEST_RE.search(path))


@dataclass
class Candidate:
    sha: str
    parent: str
    message: str
    code_files: list = field(default_factory=list)
    test_files: list = field(default_factory=list)
    solution_patch: str = ""
    test_patch: str = ""
    # 验证后填充
    valid: bool = False
    reject_reason: str = ""
    f2p: list = field(default_factory=list)
    p2p: list = field(default_factory=list)


# ───────────────────────────────────────────────── 第一步：挖候选
def list_commits(root: Path) -> list:
    out = sh("git log --reverse --format='%H|%P|%s'", root).stdout.strip().splitlines()
    rows = []
    for line in out:
        sha, parents, msg = line.split("|", 2)
        if not parents.strip():
            continue  # 跳过 initial commit
        rows.append((sha, parents.split()[0], msg))
    return rows


def split_patch(root: Path, sha: str, parent: str) -> Candidate:
    files = sh(f"git diff --name-only {parent} {sha}", root).stdout.split()
    code = [f for f in files if Path(f).suffix in CODE_EXT and not is_test_file(f)]
    tests = [f for f in files if is_test_file(f)]
    c = Candidate(
        sha=sha,
        parent=parent,
        message=sh(f"git log -1 --format=%s {sha}", root).stdout.strip(),
        code_files=code,
        test_files=tests,
    )
    if code:
        c.solution_patch = sh(
            f"git diff {parent} {sha} -- {' '.join(code)}", root
        ).stdout
    if tests:
        c.test_patch = sh(f"git diff {parent} {sha} -- {' '.join(tests)}", root).stdout
    return c


def mine(root: Path) -> list:
    return [split_patch(root, sha, par) for sha, par, _ in list_commits(root)]


# ───────────────────────────────────────────────── 第二步：便宜的启发式过滤
def cheap_filter(c: Candidate) -> Candidate:
    """**先做免费的过滤，再做贵的执行验证。** 执行一次要几分钟到几十分钟，
    而这些检查是微秒级的。真实 pipeline 里这一步能砍掉 80%+ 的候选。"""
    if not c.code_files:
        c.reject_reason = "只改了测试或文档，没有 solution patch"
    elif not c.test_files:
        c.reject_reason = "没有测试改动 → 无法自动验证"
    elif len(c.code_files) > 20:
        c.reject_reason = "改动面过大（>20 文件），多半是重构/版本升级"
    elif (
        sum(
            1
            for ln in c.solution_patch.splitlines()
            if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))
        )
        > 400
    ):
        c.reject_reason = "solution patch 超过 400 行"
    return c


# ───────────────────────────────────────────────── 第三步：执行验证
def run_tests(root: Path) -> dict:
    """返回 {test_id: 'passed'|'failed'|'error'}。真实 pipeline 里要按语言
    换 runner 并优先用结构化报告（pytest 的 -q 输出、JUnit XML）。"""
    r = subprocess.run(
        f"{PYTEST} -q --tb=no -p no:cacheprovider",
        cwd=str(root),
        shell=True,
        capture_output=True,
        text=True,
    )
    out = {}
    for line in (r.stdout + r.stderr).splitlines():
        m = re.match(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR)", line)
        if m:
            out[m.group(1)] = m.group(2).lower()
    if not out:  # -q 模式不打印每条，改用 --tb=no -v 兜底
        r = subprocess.run(
            f"{PYTEST} -v --tb=no -p no:cacheprovider",
            cwd=str(root),
            shell=True,
            capture_output=True,
            text=True,
        )
        for line in (r.stdout + r.stderr).splitlines():
            m = re.match(r"^(\S+::\S+)\s+(PASSED|FAILED|ERROR)", line)
            if m:
                out[m.group(1)] = m.group(2).lower()
    return out


def apply_patch(root: Path, patch: str) -> bool:
    if not patch.strip():
        return True
    p = root / ".__patch"
    p.write_text(patch)
    r = sh("git apply --whitespace=nowarn .__patch", root, check=False)
    p.unlink(missing_ok=True)
    return r.returncode == 0


def validate(root: Path, c: Candidate) -> Candidate:
    """三步验证。**每一步都真的跑测试**，不是猜。"""
    if c.reject_reason:
        return c
    # -f 强制丢弃上一轮打进去的补丁；-x 连 .pytest_cache 一起清
    sh(f"git checkout -q -f {c.parent} && git clean -qfdx", root)

    before_base = run_tests(root)  # ① parent 上的基线
    if not before_base:
        c.reject_reason = "① parent 上收集不到测试（环境坏了）"
        return c
    if any(v != "passed" for v in before_base.values()):
        # SWE-bench 要求这里全过。有的 pipeline 放宽成「记录下来当作已知失败」
        c.reject_reason = "① parent 上就有测试不过 —— 环境或仓库状态不干净"
        return c

    if not apply_patch(root, c.test_patch):  # ② 只打测试补丁
        c.reject_reason = "② test patch 打不上"
        return c
    before = run_tests(root)

    if not apply_patch(root, c.solution_patch):  # ③ 再打代码补丁
        c.reject_reason = "③ solution patch 打不上"
        return c
    after = run_tests(root)

    c.f2p = sorted(
        t
        for t, s in after.items()
        if s == "passed" and before.get(t) in ("failed", "error", None)
    )
    c.p2p = sorted(
        t for t, s in after.items() if s == "passed" and before.get(t) == "passed"
    )
    fails = [t for t, s in after.items() if s != "passed"]

    if fails:
        c.reject_reason = f"③ 打了 fix 之后仍有 {len(fails)} 个测试不过"
    elif not c.f2p:
        c.reject_reason = "没有 F2P 测试 —— 这个改动没有可验证的行为变化"
    else:
        c.valid = True
    return c


def to_instance(root: Path, c: Candidate) -> dict:
    """落成训练实例。**注意 problem_statement 这里是 commit message** ——
    真实数据里应该用链接的 issue 正文；拿不到 issue 时
    SWE-rebench V2 的做法是用 PR description，并单独标记来源。"""
    return {
        "instance_id": f"toy__calc-{c.sha[:7]}",
        "repo": "toy/calc",
        "base_commit": c.parent,
        "problem_statement": c.message,  # ← 真实场景换成 issue body
        "patch": c.solution_patch,  # gold patch（训练时不给模型看）
        "test_patch": c.test_patch,
        "FAIL_TO_PASS": c.f2p,
        "PASS_TO_PASS": c.p2p,
        "meta": {
            "n_code_files": len(c.code_files),
            "patch_lines": sum(
                1
                for ln in c.solution_patch.splitlines()
                if ln[:1] in "+-" and ln[:3] not in ("+++", "---")
            ),
            "problem_source": "commit_message",
        },
    }


def run(root: Path = None) -> list:
    root = root or toyrepo.build()
    cands = [cheap_filter(c) for c in mine(root)]
    print(f"挖到 {len(cands)} 个 commit（不含 initial）")
    print(
        f"  便宜过滤后剩 {sum(1 for c in cands if not c.reject_reason)} 个进入执行验证"
    )
    out = []
    for c in cands:
        validate(root, c)
        tag = "✅" if c.valid else "❌"
        detail = f"F2P={len(c.f2p)} P2P={len(c.p2p)}" if c.valid else c.reject_reason
        print(f"  {tag} {c.sha[:7]} {c.message[:52]:<52} {detail}")
        if c.valid:
            out.append(to_instance(root, c))
    sh("git checkout -q -f main && git clean -qfdx", root)
    print(f"\n最终 {len(out)} 个可用实例（产出率 {len(out) / len(cands):.0%}）")
    return out


if __name__ == "__main__":
    inst = run()
    Path("/tmp/swe_instances.json").write_text(json.dumps(inst, indent=2))
    print("已写入 /tmp/swe_instances.json")
    if inst:
        e = dict(inst[0])
        e["patch"] = e["patch"][:200] + " ...(截断)"
        e["test_patch"] = e["test_patch"][:160] + " ...(截断)"
        print("\n样例实例：\n" + json.dumps(e, indent=2, ensure_ascii=False)[:1100])
```




## rollout_cost.py

```python
"""SWE agent rollout 的推理成本：**prefix cache 是不是开着，差 20 倍。**

    python rollout_cost.py

造 SWE 训练数据时，真正的瓶颈不是 GPU 算力，是**你有没有把多轮对话的
prefix cache 用对**。这个文件把账算出来。

核心事实：agent loop 每一轮都要**重发整段历史**。
    第 t 轮的 prompt 长度 ≈ base + Σ(前 t-1 轮的所有内容)
    → 不缓存时 prefill 总量是 **O(T²)**
    → 完美缓存时只有新增部分要算，**O(T)**

40 轮的 SWE 任务上，这个差是 20 倍以上。而缓存**极其容易被无意中打掉**。
"""

from __future__ import annotations

# ── 一个典型的 SWE agent rollout（数量级取自真实 harness）
SYS_TOOLS = 3_000  # system prompt + 工具 schema（**稳定**，最该被缓存的部分）
REPO_CTX = 6_000  # 仓库结构 / 相关文件摘要（每个任务固定）
AGENT_OUT = 300  # 每轮 agent 输出（thinking + tool call）
TOOL_OUT = 800  # 每轮工具返回（文件内容、测试输出）
TURNS = 40
PER_TURN = AGENT_OUT + TOOL_OUT


def prefill_no_cache(turns=TURNS) -> int:
    """每轮从头 prefill 整段历史。Σ(base + t·per_turn) —— **二次增长**。"""
    base = SYS_TOOLS + REPO_CTX
    return sum(base + t * PER_TURN for t in range(turns))


def prefill_perfect_cache(turns=TURNS) -> int:
    """只有**新增的 token** 需要 prefill。base 只算一次。

    注意是 `turns - 1`：最后一轮的 agent 输出不会再被 prefill 了
    （它是生成出来的，不需要再喂回去）。第一版写成 `turns` 导致
    「从不失效」和「完美缓存」对不上一个 PER_TURN —— 口径不一致的经典表现。
    """
    return SYS_TOOLS + REPO_CTX + (turns - 1) * PER_TURN


def prefill_with_invalidations(turns=TURNS, break_at=()) -> int:
    """`break_at` 里的轮次缓存失效 —— 那一轮要把**当时的整段 prompt** 重算。

    正确性检查（写在这里是因为我第一版算错过）：
      break_at = 全部轮次  →  必须**恰好等于** prefill_no_cache（缓存永不命中 = 没缓存）
      break_at = ()        →  必须等于 prefill_perfect_cache
    第一版每轮既加了 `live` 又加了 `PER_TURN`，把新增 token 重复计了一次，
    结果「每轮失效」比「不开缓存」还贵 —— 那在物理上不可能。
    """
    total, live = 0, 0  # live = 已在缓存里的前缀长度
    prompt = SYS_TOOLS + REPO_CTX
    for t in range(turns):
        if live == 0 or t in break_at:
            total += prompt  # 整段 prefill
        else:
            total += prompt - live  # 只算新增
        live = prompt
        prompt += PER_TURN
    return total


def prefill_sticky(turns=TURNS, replicas=8) -> int:
    """**没有 cache-aware 路由**时，同一会话的下一轮落到别的副本上，缓存全丢。

    命中概率 ≈ 1/replicas（round-robin）。llm-d 实测：8 pods / 16 H100 上，
    prefix-cache-aware 路由 vs round-robin，**TTFT 快 57×、吞吐 2×**。
    SGLang RadixAttention + sticky 把命中率从 18% 拉到 71%。
    """
    p_hit = 1.0 / replicas
    total, live = 0.0, 0
    prompt = SYS_TOOLS + REPO_CTX
    for _ in range(turns):
        if live == 0:
            total += prompt
        else:  # 期望：命中只算新增，未命中整段重算
            total += p_hit * (prompt - live) + (1 - p_hit) * prompt
        live = prompt
        prompt += PER_TURN
    return int(total)


def trace(turns=12, break_at=(), width=58):
    """**逐轮打印**：这一轮的 prompt 有多长、其中多少是缓存里已有的、
    真正要 prefill 多少。O(T²) 这件事光看公式没感觉，看这张表就有了。"""
    print("轮次   prompt长度   缓存命中     实际prefill   累计prefill")
    print("─" * width)
    total, live = 0, 0
    prompt = SYS_TOOLS + REPO_CTX
    for t in range(turns):
        miss = (live == 0) or (t in break_at)
        this = prompt if miss else prompt - live
        total += this
        flag = ""
        if t in break_at:
            flag = "  ← 缓存失效，整段重算"
        elif live == 0:
            flag = "  ← 第一轮，本来就要全算"
        print(
            "{:>3}   {:>9,}   {:>9,}   {:>11,}   {:>11,}{}".format(
                t, prompt, 0 if miss else live, this, total, flag
            )
        )
        live = prompt
        prompt += PER_TURN
    print("─" * width)
    print(f"      最终 prompt {prompt - PER_TURN:,} tokens，累计 prefill {total:,}")
    return total


def fmt(n) -> str:
    return f"{n / 1e6:.2f}M" if n >= 1e6 else f"{n / 1e3:.0f}k"


def main():
    import sys as _s

    if "--trace" in _s.argv:
        print("═══ 有缓存：每轮只 prefill 新增的 1,100 token ═══\n")
        a = trace(12)
        print("\n═══ 无缓存（比如 system prompt 里有时间戳）═══\n")
        b = trace(12, break_at=tuple(range(12)))
        print(
            f"\n12 轮就差了 {b / a:.1f} 倍；40 轮差 {prefill_no_cache() / prefill_perfect_cache():.1f} 倍。"
        )
        print("**注意增长形状**：有缓存那列是常数 1,100；无缓存那列每轮多 1,100。")
        return

    base = prefill_no_cache()
    best = prefill_perfect_cache()

    print("═══ 一个 40 轮 SWE rollout 的 prefill token 量 ═══\n")
    rows = [
        ("① 不开 prefix cache", base),
        ("② 完美 prefix cache", best),
        (
            "③ 完美缓存 + 中途 compact 一次（第 25 轮）",
            prefill_with_invalidations(break_at=(25,)),
        ),
        (
            "④ 完美缓存 + compact 三次（10/20/30）",
            prefill_with_invalidations(break_at=(10, 20, 30)),
        ),
        (
            "⑤ system prompt 里有时间戳（**每轮都失效**）",
            prefill_with_invalidations(break_at=tuple(range(TURNS))),
        ),
        ("⑥ 开了缓存但**没有 sticky 路由**（8 副本 round-robin）", prefill_sticky()),
    ]
    print("{:<44} {:>9} {:>10}".format("配置", "prefill", "vs 最优"))
    print("─" * 66)
    for name, v in rows:
        print("{:<44} {:>9} {:>9.1f}×".format(name, fmt(v), v / best))

    print(f"\n⭐ 开不开缓存差 **{base / best:.0f} 倍**。")
    print("   而 ⑤ 说明：**system prompt 里一个时间戳，就能让缓存完全失效**")
    print(
        f"   （{fmt(prefill_with_invalidations(break_at=tuple(range(TURNS))))} "
        f"≈ 不开缓存的 {prefill_with_invalidations(break_at=tuple(range(TURNS))) / base:.1f} 倍）。"
    )
    print("   ⑥ 说明：**开了缓存不等于用上了缓存** —— 没有 cache-aware 路由，")
    print("   多副本部署下命中率约 1/N。llm-d 实测 sticky 路由 TTFT 快 57×。")

    # ── n 个样本共享前缀
    print("\n═══ RL rollout：每个任务采 n 个样本 ═══\n")
    n = 8
    sep = n * best
    shared = best + (n - 1) * (TURNS * PER_TURN)  # 只有分叉之后的部分要重算
    print(f"  n={n} 个独立请求      {fmt(sep):>8}")
    print(f"  n={n} 共享 base 前缀  {fmt(shared):>8}   省 {(1 - shared / sep):.0%}")
    print("  → 用引擎的 `n=8` 参数（或 SGLang 的 fork），别发 8 个独立请求。")
    print(
        f"  ⚠️ **但这只值 {(1 - shared / sep):.0%}，不是大头** —— n 个样本在第一轮就分叉了，"
    )
    print("     之后什么都不共享。真正的 23× 来自**单条轨迹内跨轮次**的缓存。")
    print("     别把 n-sharing 当成主要优化。")

    # ── 真正被忽略的大头：跨任务共享仓库上下文
    print("\n═══ 跨任务：**按仓库分组调度** ═══\n")
    tasks_per_repo = 40
    print(f"  同一个仓库的 {tasks_per_repo} 个任务共享 {fmt(REPO_CTX)} 的仓库上下文")
    print(
        f"    随机打散调度：每个任务各自 prefill 一次 → "
        f"{fmt(tasks_per_repo * REPO_CTX)}"
    )
    print(f"    按仓库分组：  只 prefill 一次              → {fmt(REPO_CTX)}")
    print(f"  ⭐ **调度顺序本身就是一个优化项。** 任务列表按 repo 排序再发，")
    print("     配合 cache-aware 路由（同 repo 打到同一副本），这部分几乎归零。")

    # ── 规模：一次数据生成 campaign
    print("\n═══ 一次数据生成 campaign 的账 ═══\n")
    n_tasks, n_samp = 5_000, 8
    for label, per in (
        ("不开缓存", base),
        ("完美缓存", best),
        ("缓存+sticky+n 共享", shared / n_samp),
    ):
        tot = n_tasks * n_samp * per
        # H100 prefill 粗估：~10k tok/s/卡（长上下文、含 attention 二次项）
        gpu_h = tot / 10_000 / 3600
        print(
            f"  {label:<20} {tot / 1e9:>7.1f}B tokens   ≈ {gpu_h:>7.0f} GPU-小时"
            f"   ≈ ${gpu_h * 2.5:>8,.0f}（按 $2.5/H100-h）"
        )
    print("\n  → **同一批数据，缓存用对与否差两个数量级的钱。**")
    print("    这就是为什么『造 SWE 数据』本质上是个推理工程问题，不是训练问题。")


if __name__ == "__main__":
    main()
```




## synth.py

````python
"""合成路线：**环境优先，再造 bug**（SWE-smith 的思路）。

挖 PR 的路线有个硬上限：一个仓库里「同时改了代码和测试、且能跑通」的 PR
就那么多。SWE-bench 从 12 个仓库只挖出 2,294 个实例；SWE-Gym 11 个仓库 2,438 个。

SWE-smith 把顺序**倒过来**：先把仓库的执行环境搭好（这才是真正贵的部分），
然后在环境里**批量制造** bug。同样 128 个仓库产出 5 万个实例，
平均每仓库 381 个，pandas 一个仓库就 2,277 个。

它用四种造 bug 的策略（我们这里实现最便宜的第 2 种）：
  1. **LM Modify / LM Rewrite** —— 让模型改坏一个函数，或只给签名+docstring 让它重写
  2. **Procedural Modification** —— 改 AST（删条件/删循环/换运算符/…共 13 种）← 本文件
  3. **Combine Bugs** —— 把同文件/同模块的多个 bug 合成一个更难的任务
  4. **Invert PR（PR Mirroring）** —— 让模型把一个真 PR 的改动「撤销」回去

**关键洞察**（论文原话的意思）：执行验证不只能验证解法，
**它也能筛出「哪些改动是真 bug」** —— 造一堆候选，只留下真的弄挂测试的那些。

    python synth.py
"""

from __future__ import annotations

import ast
import difflib
import json
import random
from pathlib import Path

import mine
import toyrepo
from toyrepo import sh


# ─────────────────────────────────────────── AST 变换（procedural）
class _Mutator(ast.NodeTransformer):
    """13 种里选 6 种代表性的。**每次只改一处** —— 多处一起改会让任务
    难度不可控，而且定位不到「这个 bug 到底是什么」。"""

    KINDS = (
        "flip_compare",
        "off_by_one",
        "drop_if",
        "drop_loop",
        "swap_binop",
        "return_none",
    )

    def __init__(self, kind: str, rng: random.Random):
        self.kind, self.rng, self.done = kind, rng, False

    def _fire(self) -> bool:
        if self.done or self.rng.random() < 0.5:
            return False
        self.done = True
        return True

    def visit_Compare(self, node):
        self.generic_visit(node)
        flip = {
            ast.Lt: ast.LtE,
            ast.LtE: ast.Lt,
            ast.Gt: ast.GtE,
            ast.GtE: ast.Gt,
            ast.Eq: ast.NotEq,
            ast.NotEq: ast.Eq,
        }
        if self.kind == "flip_compare" and type(node.ops[0]) in flip and self._fire():
            node.ops = [flip[type(node.ops[0])]()]
        return node

    def visit_Constant(self, node):
        if (
            self.kind == "off_by_one"
            and isinstance(node.value, int)
            and not isinstance(node.value, bool)
            and self._fire()
        ):
            return ast.copy_location(
                ast.Constant(value=node.value + self.rng.choice([-1, 1])), node
            )
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        if self.kind == "drop_if" and node.body and self._fire():
            return node.body  # 把 if 拆掉，body 无条件执行
        return node

    def visit_For(self, node):
        self.generic_visit(node)
        if self.kind == "drop_loop" and self._fire():
            return ast.copy_location(ast.Pass(), node)
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        swap = {
            ast.Add: ast.Sub,
            ast.Sub: ast.Add,
            ast.Mult: ast.Div,
            ast.Div: ast.Mult,
            ast.FloorDiv: ast.Div,
        }
        if self.kind == "swap_binop" and type(node.op) in swap and self._fire():
            node.op = swap[type(node.op)]()
        return node

    def visit_Return(self, node):
        self.generic_visit(node)
        if self.kind == "return_none" and node.value is not None and self._fire():
            return ast.copy_location(ast.Return(value=ast.Constant(None)), node)
        return node


def mutate(src: str, kind: str, seed: int):
    """返回改坏后的源码；没改动则返回 None。"""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    m = _Mutator(kind, random.Random(seed))
    new = m.visit(tree)
    if not m.done:
        return None
    ast.fix_missing_locations(new)
    try:
        out = ast.unparse(new)  # py3.9+
    except Exception:
        return None
    return out if out.strip() != src.strip() else None


# ─────────────────────────────────────────── 生成 + 执行验证
def synthesize(
    root: Path,
    targets=("calc/stats.py", "calc/text.py"),
    per_file: int = 12,
    verbose: bool = True,
) -> list:
    sh("git checkout -q -f main && git clean -qfdx", root)
    base_tests = mine.run_tests(root)
    assert base_tests and all(v == "passed" for v in base_tests.values()), (
        "环境必须先是干净的 —— 这是 SWE-smith 第一步「建环境」的验收标准"
    )
    if verbose:
        print(f"基线：{len(base_tests)} 个测试全过\n")

    kept, tried = [], 0
    for rel in targets:
        orig = (root / rel).read_text()
        for i in range(per_file):
            kind = _Mutator.KINDS[i % len(_Mutator.KINDS)]
            bugged = mutate(orig, kind, seed=i)
            tried += 1
            if bugged is None:
                continue
            (root / rel).write_text(bugged)
            res = mine.run_tests(root)
            (root / rel).write_text(orig)  # 立刻还原

            broke = sorted(t for t, s in res.items() if s != "passed")
            still = sorted(t for t, s in res.items() if s == "passed")
            if not res:
                continue  # 语法/导入直接崩，丢弃
            if not broke:
                continue  # 没弄挂任何测试 → 不是 bug
            if len(broke) == len(res):
                continue  # 全挂了 → 多半是导入炸了，太粗暴
            kept.append(
                {
                    "instance_id": f"synth__calc-{rel.split('/')[-1][:-3]}-{kind}-{i}",
                    "repo": "toy/calc",
                    "strategy": f"procedural:{kind}",
                    "bugged_file": rel,
                    # 存**统一 diff** 而不是整份文件。第一版我存了整份源码，
                    # 结果 curate 里的 normalize_patch（只保留 +/- 行）返回空串，
                    # 所有实例的 MinHash 签名一模一样 → 去重把它们全判成重复。
                    # **两个数据源 schema 不一致，会让下游过滤静默失效。**
                    "bug_patch": "".join(
                        difflib.unified_diff(
                            orig.splitlines(keepends=True),
                            bugged.splitlines(keepends=True),
                            fromfile=f"a/{rel}",
                            tofile=f"b/{rel}",
                        )
                    ),
                    "FAIL_TO_PASS": broke,
                    "PASS_TO_PASS": still,
                    "problem_statement": None,  # 下一步由 LM 生成 issue 文本
                }
            )
    sh("git checkout -q -f main && git clean -qfdx", root)
    if verbose:
        print(
            f"尝试 {tried} 次变异 → **{len(kept)} 个有效 bug**（产出率 {len(kept) / tried:.0%}）"
        )
        from collections import Counter

        for k, v in Counter(x["strategy"] for x in kept).most_common():
            print(f"  {k:<28} {v}")
    return kept


def draft_issue(inst: dict) -> str:
    """真实做法（SWE-smith §D）：把 `.diff`、一个随机 F2P 测试的源码、
    以及带 bug 跑测试的输出一起喂给 LM，让它写成 GitHub issue 风格，
    **并且包含基于 F2P 测试的复现代码**。成本约 2.54 美分一条。

    这里给一个不调模型的占位版本，说明需要哪些字段。"""
    t = inst["FAIL_TO_PASS"][0]
    return (
        f"### Unexpected behaviour in `{inst['bugged_file']}`\n\n"
        f"After upgrading, `{t.split('::')[-1]}` no longer behaves as documented.\n\n"
        f"**To reproduce**\n```bash\npytest {t}\n```\n\n"
        f"**Expected**: the assertion holds.  **Actual**: it fails."
    )


if __name__ == "__main__":
    root = toyrepo.build()
    out = synthesize(root)
    for o in out:
        o["problem_statement"] = draft_issue(o)
    Path("/tmp/swe_synth.json").write_text(json.dumps(out, indent=2))
    print(f"\n对比：挖 PR 只得到 5 个实例；同一个仓库合成得到 {len(out)} 个。")
    print("这就是 SWE-smith 「128 个仓库 → 5 万实例」的机制。")
    if out:
        e = out[0]
        print(
            f"\n样例：{e['instance_id']}\n  策略 {e['strategy']}"
            f"\n  F2P {e['FAIL_TO_PASS']}\n  P2P {len(e['PASS_TO_PASS'])} 个"
        )
````




## test_swe_data.py

```python
"""锁住整条 pipeline 的关键不变量。`pytest test_swe_data.py -q`"""

from __future__ import annotations

import pytest

import curate
import github
import mine
import synth
import toyrepo

ROOT = toyrepo.build()
INSTANCES = mine.run(ROOT)


# ───────────────────────────── 挖掘 + 执行验证
def test_yield_matches_ground_truth():
    """玩具仓库里我知道正确答案 —— 5 个合格、3 个该被过滤。"""
    assert len(INSTANCES) == toyrepo.EXPECTED_VALID


def test_every_instance_has_f2p_and_p2p():
    """没有 F2P 就没有 reward；没有 P2P 就没有防回归护栏。"""
    for i in INSTANCES:
        assert i["FAIL_TO_PASS"], i["instance_id"]
        assert isinstance(i["PASS_TO_PASS"], list)
        assert not set(i["FAIL_TO_PASS"]) & set(i["PASS_TO_PASS"])


def test_docs_only_and_test_only_commits_are_rejected():
    ids = {i["instance_id"] for i in INSTANCES}
    msgs = {i["problem_statement"] for i in INSTANCES}
    assert not any(m.startswith(("docs:", "test:", "chore:")) for m in msgs)
    assert len(ids) == len(INSTANCES)


def test_solution_patch_never_touches_test_files():
    """**gold patch 里混进测试文件 = 答案泄漏。** 训练时模型能直接看到断言。"""
    for i in INSTANCES:
        for line in i["patch"].splitlines():
            if line.startswith("+++ b/"):
                assert not mine.is_test_file(line[6:]), i["instance_id"]


def test_test_patch_only_touches_test_files():
    for i in INSTANCES:
        for line in i["test_patch"].splitlines():
            if line.startswith("+++ b/"):
                assert mine.is_test_file(line[6:]), i["instance_id"]


@pytest.mark.parametrize(
    "path,expected",
    [
        ("tests/test_a.py", True),
        ("src/test_utils.py", True),
        ("pkg/foo_test.py", True),
        ("testing/conftest.py", True),
        ("src/core.py", False),
        ("docs/index.md", False),
    ],
)
def test_test_file_regex(path, expected):
    assert mine.is_test_file(path) is expected


@pytest.mark.parametrize(
    "path", ["src/contest.py", "build/latest/x.py", "app/protests/views.py"]
)
def test_anchored_regex_beats_the_papers_substring_match(path):
    """SWE-rebench V2 用的是无锚定子串匹配 `(?i)(test(?:ing|s)?|e2e)`，
    这三个路径会被它误判成测试文件 —— 后果是这些文件的改动被当成 test_patch，
    **真正的 solution patch 变空，实例被静默丢弃**。加路径段边界就好了。"""
    assert mine.NAIVE_TEST_RE.search(path), "论文那条确实会误判"
    assert mine.is_test_file(path) is False, "加了锚定之后不该误判"


# ───────────────────────────── 合成
def test_synth_yields_more_than_mining():
    """合成路线的全部意义：同一个仓库产出更多实例。"""
    s = synth.synthesize(ROOT, verbose=False)
    assert len(s) >= len(INSTANCES)


def test_every_synth_bug_actually_breaks_a_test():
    """**执行验证不只验证解法，也用来筛「哪些改动是真 bug」。**"""
    for s in synth.synthesize(ROOT, verbose=False):
        assert s["FAIL_TO_PASS"] and s["PASS_TO_PASS"]


def test_mutation_is_deterministic():
    src = "def f(x):\n    return x + 1\n"
    a = synth.mutate(src, "swap_binop", 0)
    b = synth.mutate(src, "swap_binop", 0)
    assert a == b


def test_synth_patch_is_a_real_diff():
    """schema 护栏：存整份源码会让下游去重静默失效（我踩过）。"""
    for s in synth.synthesize(ROOT, verbose=False):
        curate.assert_is_diff(s["bug_patch"], s["instance_id"])


# ───────────────────────────── curate
def test_dedup_catches_identical_patches():
    a = dict(INSTANCES[0])
    b = dict(INSTANCES[0])
    b["instance_id"] = "clone"
    kept, dropped = curate.dedup([a, b])
    assert len(kept) == 1 and len(dropped) == 1


def test_dedup_keeps_genuinely_different_patches():
    kept, _ = curate.dedup(INSTANCES)
    assert len(kept) >= len(INSTANCES) - 1


def test_empty_normalization_raises_instead_of_silently_deduping():
    with pytest.raises(ValueError):
        curate.assert_is_diff("def f():\n    return 1\n", "not-a-diff")


def test_decontamination_removes_benchmark_repos():
    fake = dict(INSTANCES[0])
    fake["repo"] = "django/django"
    kept, removed = curate.decontaminate([fake])
    assert not kept and "benchmark" in removed[0][1]


def test_decontamination_catches_near_duplicate_patch():
    kept, removed = curate.decontaminate(
        [INSTANCES[0]], bench_repos=frozenset(), bench_patches=[INSTANCES[0]["patch"]]
    )
    assert not kept


def test_empirical_difficulty_drops_zero_and_one():
    """pass@k ∈ {0,1} 的题在 GRPO 里组内优势全为 0 —— 白烧算力。"""
    assert curate.empirical_difficulty({}, [0] * 8)["keep_for_rl"] is False
    assert curate.empirical_difficulty({}, [1] * 8)["keep_for_rl"] is False
    assert curate.empirical_difficulty({}, [0, 1, 0, 0])["keep_for_rl"] is True


# ───────────────────────────── 仓库筛选
def test_repo_filter_excludes_benchmark_and_forks():
    by = {r["repo"]: r for r in map(github.score_repo, github.SAMPLE)}
    assert not by["pallets/flask"]["keep"]  # benchmark 测试仓库
    assert not by["acme/fastapi-clone"]["keep"]  # fork
    assert not by["corp/internal-tool"]["keep"]  # 非宽松 license
    assert by["tqdm/tqdm"]["keep"]


def test_linked_issue_requires_resolving_verb():
    assert github.linked_issue_numbers("Fixes #1, closes #2") == [1, 2]
    assert github.linked_issue_numbers("related to #3") == []
```




## toyrepo.py

```python
"""造一个带**真实 git 历史**的玩具仓库，供整条 pipeline 跑在上面。

为什么要造而不是 clone 真仓库：
  * 真仓库要装依赖、跑几分钟、要网络 —— 学 pipeline 的时候这些全是噪声
  * 玩具仓库里我**知道正确答案**（哪几个 commit 该被挖出来），可以写断言
  * 它埋了真实世界会遇到的四种「不合格」commit，正好用来练过滤

产出：一个 /tmp 下的 git repo，8 个 commit：
    5 个合格候选（改代码 + 改测试，且测试真的从 fail 变 pass）
    3 个不合格（只改文档 / 只改测试 / 改代码但没加测试）
"""

from __future__ import annotations

import shutil
import subprocess
import textwrap
from pathlib import Path

DEFAULT = Path("/tmp/swe_toyrepo")


def sh(cmd, cwd, check=True):
    return subprocess.run(
        cmd, cwd=str(cwd), shell=True, capture_output=True, text=True, check=check
    )


def _w(root: Path, rel: str, body: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip())


def _append(root: Path, rel: str, body: str):
    """追加时必须**单独** dedent 新块 —— 直接 read_text()+body 再整体 dedent
    会因为已有内容顶格而使公共前缀为空，新块的缩进被原样保留 → IndentationError。
    （我第一版就是这么写的，pytest 直接 collection error。）"""
    p = root / rel
    p.write_text(p.read_text().rstrip() + "\n\n" + textwrap.dedent(body).strip() + "\n")


def _commit(root: Path, msg: str, date: str):
    sh("git add -A", root)
    env = f'GIT_AUTHOR_DATE="{date}" GIT_COMMITTER_DATE="{date}"'
    sh(f'{env} git commit -q -m {msg!r}', root)


def build(root: Path = DEFAULT) -> Path:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    sh("git init -q -b main", root)
    sh('git config user.email a@b.c && git config user.name Dev', root)

    # ── c0：初始版本，四个函数各带一个 bug ───────────────────────────
    _w(root, "calc/__init__.py", "")
    _w(
        root,
        "calc/stats.py",
        '''
        def mean(xs):
            return sum(xs) / len(xs)                    # BUG: 空列表除零

        def median(xs):
            s = sorted(xs)
            return s[len(s) // 2]                       # BUG: 偶数长度不取平均

        def clamp(x, lo, hi):
            return max(lo, min(x, hi))
    ''',
    )
    _w(
        root,
        "calc/text.py",
        '''
        def slugify(s):
            return s.lower().replace(" ", "-")          # BUG: 没去掉标点

        def truncate(s, n):
            return s[:n]                                # BUG: 没加省略号
    ''',
    )
    _w(
        root,
        "tests/test_stats.py",
        '''
        from calc.stats import clamp

        def test_clamp():
            assert clamp(5, 0, 3) == 3
    ''',
    )
    _w(root, "README.md", "# calc\n\nTiny numeric helpers.\n")
    _commit(root, "initial commit", "2025-01-06T10:00:00")

    # ── 合格候选 ×5：改代码 + 加测试 ─────────────────────────────────
    _w(
        root,
        "calc/stats.py",
        '''
        def mean(xs):
            if not xs:
                raise ValueError("mean() of empty sequence")
            return sum(xs) / len(xs)

        def median(xs):
            s = sorted(xs)
            return s[len(s) // 2]

        def clamp(x, lo, hi):
            return max(lo, min(x, hi))
    ''',
    )
    _w(
        root,
        "tests/test_stats.py",
        '''
        import pytest
        from calc.stats import clamp, mean

        def test_clamp():
            assert clamp(5, 0, 3) == 3

        def test_mean_empty_raises():
            with pytest.raises(ValueError):
                mean([])
    ''',
    )
    _commit(
        root,
        "fix: mean() crashes with ZeroDivisionError on empty input",
        "2025-01-09T11:00:00",
    )

    _w(
        root,
        "calc/stats.py",
        (root / "calc/stats.py")
        .read_text()
        .replace(
            "    s = sorted(xs)\n    return s[len(s) // 2]",
            "    s = sorted(xs)\n    m = len(s) // 2\n"
            "    return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2",
        ),
    )
    _append(
        root,
        "tests/test_stats.py",
        '''
        def test_median_even_length():
            from calc.stats import median
            assert median([1, 2, 3, 4]) == 2.5
    ''',
    )
    _commit(root, "fix: median() wrong for even-length input", "2025-01-14T09:30:00")

    _w(
        root,
        "calc/text.py",
        '''
        import re

        def slugify(s):
            s = re.sub(r"[^\\w\\s-]", "", s.lower())
            return re.sub(r"[\\s_]+", "-", s).strip("-")

        def truncate(s, n):
            return s[:n]
    ''',
    )
    _w(
        root,
        "tests/test_text.py",
        '''
        from calc.text import slugify

        def test_slugify_strips_punctuation():
            assert slugify("Hello, World!") == "hello-world"
    ''',
    )
    _commit(root, "fix: slugify keeps punctuation in the slug", "2025-01-20T15:12:00")

    _w(
        root,
        "calc/text.py",
        (root / "calc/text.py")
        .read_text()
        .replace(
            "def truncate(s, n):\n    return s[:n]",
            'def truncate(s, n):\n'
            '    return s if len(s) <= n else s[: max(0, n - 1)] + "\\u2026"',
        ),
    )
    _append(
        root,
        "tests/test_text.py",
        '''
        def test_truncate_adds_ellipsis():
            from calc.text import truncate
            assert truncate("abcdef", 4) == "abc\\u2026"
            assert truncate("ab", 4) == "ab"
    ''',
    )
    _commit(root, "fix: truncate() should append an ellipsis", "2025-01-27T18:03:00")

    _w(
        root,
        "calc/stats.py",
        (root / "calc/stats.py")
        .read_text()
        .replace(
            "def clamp(x, lo, hi):\n    return max(lo, min(x, hi))",
            "def clamp(x, lo, hi):\n"
            "    if lo > hi:\n"
            "        raise ValueError('lo must be <= hi')\n"
            "    return max(lo, min(x, hi))",
        ),
    )
    _append(
        root,
        "tests/test_stats.py",
        '''
        def test_clamp_rejects_inverted_bounds():
            import pytest
            from calc.stats import clamp
            with pytest.raises(ValueError):
                clamp(1, 5, 0)
    ''',
    )
    _commit(
        root, "fix: clamp silently returns garbage when lo > hi", "2025-02-03T08:45:00"
    )

    # ── 不合格 ×3：pipeline 必须把它们过滤掉 ──────────────────────────
    _w(
        root,
        "README.md",
        "# calc\n\nTiny numeric helpers.\n\n## Install\n\n`pip install -e .`\n",
    )
    _commit(root, "docs: add install section", "2025-02-05T12:00:00")  # 只改文档

    _append(
        root,
        "tests/test_text.py",
        '''
        def test_slugify_idempotent():
            from calc.text import slugify
            assert slugify(slugify("A B")) == slugify("A B")
    ''',
    )
    _commit(
        root, "test: add idempotence check for slugify", "2025-02-07T14:20:00"
    )  # 只改测试

    _w(
        root,
        "calc/stats.py",
        (root / "calc/stats.py")
        .read_text()
        .replace("def mean(xs):", "def mean(xs):\n    # NOTE: raises on empty input"),
    )
    _commit(
        root, "chore: clarify mean() docstring", "2025-02-10T16:00:00"
    )  # 改代码无测试

    return root


# 期望结果 —— 用来写断言。**没有 ground truth 的 pipeline 没法调试。**
EXPECTED_VALID = 5
EXPECTED_TOTAL_COMMITS = 9  # 含 initial


if __name__ == "__main__":
    r = build()
    log = sh("git log --oneline", r).stdout.strip().splitlines()
    print(f"建好了 {r}，{len(log)} 个 commit：")
    for line in reversed(log):
        print("  " + line)
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/labs/swe_data/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/swe_data/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
