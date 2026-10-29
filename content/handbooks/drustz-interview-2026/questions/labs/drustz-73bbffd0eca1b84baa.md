---
id: drustz-73bbffd0eca1b84baa
section: labs
order: 14
level: A
title: cr_data · Code review agent 的数据 pipeline（可跑）
quick: 作者完整文档 · cr_data · Code review agent 的数据 pipeline（可跑）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/cr_data/README.md
    type: primary
---
# cr_data · Code review agent 的数据 pipeline（可跑）

配套文章：[`../../22_code_review_agent_data.md`](?book=drustz-interview-2026&section=mlsd&question=drustz-3b050f56a2ca44e09d)

```bash
V=/Users/mingrui/Documents/codes/interview/.venv/bin/python
$V toyreview.py                 # 造语料：git 历史 + 19 条 review 评论 + ground truth
$V signals.py                   # ① 采纳信号（真 git diff）② SZZ（真 git blame）
$V gate.py                      # 过滤漏斗 + **校准自动信号**
$V pairs.py                     # 正负样本（含「未评论行」陷阱组）+ 偏好对
$V reward.py                    # 分层 reward + 精度优先 + 防 hack
$V -m pytest test_cr_data.py -q # 20 passed
```



只依赖 numpy + pytest。**采纳信号和 SZZ 都是真的调 git 算出来的。**

| 文件 | 干什么 | 对应文章 |
|---|---|---|
| `toyreview.py` | 语料：6 个 commit + 19 条评论（8 条真信号、11 条五类噪声）+ ground truth | §2 |
| `signals.py` | **制造可验证性**：采纳信号 + SZZ 回溯 | §3 |
| `gate.py` | 过滤（bot/nit/夸奖/提问/重复）+ **calibration**（precision/recall vs 人工标注） | §4 |
| `pairs.py` | 三类正样本（按证据强度）+ 四类负样本 + 一个陷阱组 | §5 |
| `reward.py` | 三层 reward、两段式精度优先、hack 监控 | §6 |

## 跑出来的四个关键结果

**① 采纳信号能算，但有 30% 假阳性**
```text
precision 70%  recall 88%  TP=7 FP=3 FN=1 TN=8
假阳性：cm07(夸奖) cm14(nit) cm17(事实错误的安全评论)
假阴性：cm03（说得对、当时没采纳，三周后变成真 bug）
```



**② SZZ 真的回溯到了引入 bug 的 commit**
```text
bug-fix 5023e36 → git blame → 由 5be7388 引入  ✅ 命中期望
可验证正样本：shop/orders.py:21 `if code == "SAVE10":`
```



**③ 词袋去重抓不到改写**
```text
阈值 0.35 → 0 条    阈值 0.10 → cm18≈cm11、cm19≈cm01
```



**④ F1 最优阈值不随误报代价变化，产品最优会变**
```text
信任衰减 0.95 → 产品最优 0.075（比 F1 宽 0.60）
信任衰减 0.75 → 恰好重合（巧合）
信任衰减 0.45 → 产品最优 0.825（比 F1 严 0.15）
F1 最优永远是 0.675
```



## 三个测试专门守着这个领域最容易犯的错

- `test_unreviewed_lines_are_kept_separate` —— 把「没人评论的行」当负样本
- `test_an_unreviewed_line_actually_contained_a_real_bug` —— 证明上一条不是洁癖
- `test_f1_optimum_ignores_false_positive_cost` —— F1 不知道误报值多少钱

## gate.py

```python
"""质量把关：**过滤噪声 + 校准你的自动信号**。

两步，顺序不能反：

  第一步 **过滤**：机器人、纯风格、提问、夸奖、过期引用、重复。
    这些在真实 PR 语料里占大头 —— 不滤掉，模型学到的是「怎么写 nit」。

  第二步 **校准**：你的自动信号（采纳率）到底有多准？
    ⭐ **这一步大多数人跳过，而它决定了后面所有训练的上限。**
    「代码后来变了」≠「因为你的评论才变的」——
    评论恰好落在一行因别的原因被改的代码上，就会被记成采纳。

    python gate.py
"""

from __future__ import annotations

import re
from collections import Counter

import numpy as np

import signals
import toyreview

BOT_SUFFIXES = ("[bot]", "-bot", "_bot")
KNOWN_BOTS = {
    "codecov",
    "sonarqube",
    "dependabot",
    "renovate",
    "coveralls",
    "github-actions",
    "stale",
    "greptile",
    "coderabbitai",
}
NIT_RE = re.compile(r"^\s*(nit|nitpick|minor|style)\s*[:\-]", re.I)
PRAISE_RE = re.compile(r"^\s*(nice|great|lgtm|looks good|👍|awesome|thanks)", re.I)
QUESTION_ONLY = re.compile(r"^[^.!]*\?\s*$")


# ─────────────────────────────────────────── 第一步：过滤
def is_bot(author: str) -> bool:
    a = author.lower()
    return any(a.endswith(s) for s in BOT_SUFFIXES) or a.split("[")[0] in KNOWN_BOTS


def classify(c: dict) -> str:
    """**只用评论本身**判类型（真实场景里这一层可以是个小分类器）。

    Atlassian 的 comment ranker 就是这么做的：**只喂评论文本**给 ModernBERT，
    标签是二元的 code-resolution outcome，就把 CRR 拉到 40–45%（人类 ~45%）。
    说明**评论的措辞本身就高度预测它会不会被采纳** —— 你甚至不需要看代码。
    """
    if is_bot(c["author"]):
        return "bot"
    b = c["body"].strip()
    if NIT_RE.match(b):
        return "nit_style"
    if PRAISE_RE.match(b):
        return "praise"
    if QUESTION_ONLY.match(b):
        return "question"
    return "substantive"


def dedup_comments(comments: list, thr: float = 0.35) -> tuple:
    """同一个 (文件, 行附近) 上语义重复的评论只留一条。

    **真实 PR 里多人重复指出同一问题非常常见** —— 不去重的话，
    高频问题会在训练集里被过度加权，模型学会反复说同一句话。
    这里用词袋 Jaccard；真实规模用 embedding + LSH。
    """

    def toks(s):
        return set(re.findall(r"[a-z]{3,}", s.lower()))

    kept, dropped = [], []
    for c in comments:
        dup = next(
            (
                k
                for k in kept
                if k["path"] == c["path"]
                and abs(k["line"] - c["line"]) <= 3
                and len(toks(k["body"]) & toks(c["body"]))
                / max(1, len(toks(k["body"]) | toks(c["body"])))
                >= thr
            ),
            None,
        )
        (dropped if dup else kept).append(
            {**c, "_dup_of": dup["comment_id"]} if dup else c
        )
    return kept, dropped


def gate(comments: list) -> dict:
    stages = {"raw": list(comments)}
    x = [c for c in comments if not is_bot(c["author"])]
    stages["去机器人"] = list(x)
    x = [c for c in x if classify(c) == "substantive"]
    stages["去 nit/夸奖/纯提问"] = list(x)
    x, dropped = dedup_comments(x)
    stages["去重复"] = list(x)
    return {"stages": stages, "dropped_dups": dropped, "final": x}


# ─────────────────────────────────────────── 第二步：校准自动信号
def calibrate(comments: list) -> dict:
    """把自动信号（resolved）当成对「有没有用」的预测，量它的 precision / recall。

    这一步需要**一批人工标注**（真实场景里就是 BitsAI-CR 的
    「每天抽样 ≤10%、每周人工标注」）。这里用 `_gt_useful` 当人工标注的替身。
    """
    y = np.array([c["_gt_useful"] for c in comments])
    p = np.array([c["signal"]["resolved"] for c in comments])
    tp = int(((p == 1) & (y == 1)).sum())
    fp = int(((p == 1) & (y == 0)).sum())
    fn = int(((p == 0) & (y == 1)).sum())
    tn = int(((p == 0) & (y == 0)).sum())
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": prec,
        "recall": rec,
        "f1": 2 * prec * rec / max(1e-9, prec + rec),
        "false_positives": [
            c["comment_id"]
            for c in comments
            if c["signal"]["resolved"] and not c["_gt_useful"]
        ],
        "false_negatives": [
            c["comment_id"]
            for c in comments
            if not c["signal"]["resolved"] and c["_gt_useful"]
        ],
    }


if __name__ == "__main__":
    built = toyreview.build()
    comments = signals.annotate(built["root"], built["comments"])

    print("═══ 第一步：过滤漏斗 ═══\n")
    g = gate(comments)
    prev = None
    for name, xs in g["stages"].items():
        delta = "" if prev is None else f"  (−{prev - len(xs)})"
        print(f"  {name:<22} {len(xs):>3} 条{delta}")
        prev = len(xs)
    print("\n  ⚠️ 语义去重：词袋 Jaccard **抓不到改写**")
    print("  {:<8} {:<6} {}".format("阈值", "命中", "配对"))
    for thr in (0.35, 0.25, 0.15, 0.10):
        _, dd = dedup_comments(g["stages"]["去 nit/夸奖/纯提问"], thr)
        pairs = "、".join(f"{d['comment_id']}≈{d['_dup_of']}" for d in dd) or "—"
        print(f"  {thr:<8.2f} {len(dd):<6} {pairs}")
    print(
        "  真值：cm18 是 cm11 的改写（都在说 MD5），cm19 是 cm01 的改写（都在说 None）。"
    )
    print("  → 阈值 0.35 一条都抓不到；降到 0.10 才抓到，但那时误伤风险已经很高。")
    print("    **原因**：两条评论说的是同一件事，用的却是完全不同的词。")
    print(
        "    词法方法在这里天然失效，**语义去重必须用 embedding**"
        "（真实规模再加 LSH 分桶）。"
    )

    kept_useful = sum(c["_gt_useful"] for c in g["final"])
    print(
        f"\n  过滤后有价值比例：{kept_useful}/{len(g['final'])} = "
        f"{kept_useful / len(g['final']):.0%}"
        f"（过滤前 {sum(c['_gt_useful'] for c in comments)}/{len(comments)} = "
        f"{sum(c['_gt_useful'] for c in comments) / len(comments):.0%}）"
    )

    print("\n═══ 第二步：校准采纳信号 ⭐ ═══\n")
    cal = calibrate(comments)
    print(f"  把「代码后来变了」当成「这条评论有用」的预测：")
    print(
        f"    precision {cal['precision']:.0%}   recall {cal['recall']:.0%}   "
        f"F1 {cal['f1']:.2f}"
    )
    print(f"    TP={cal['tp']}  FP={cal['fp']}  FN={cal['fn']}  TN={cal['tn']}")
    print(f"\n  **假阳性**（代码变了但评论没用）：{cal['false_positives']}")
    for cid in cal["false_positives"]:
        c = next(x for x in comments if x["comment_id"] == cid)
        print(f"    {cid} [{c['type']}] 「{c['body'][:56]}…」")
    print("  → 机制：评论恰好落在**因别的原因被改动**的那一行上。")
    print("    最危险的是其中事实错误的那条 —— 它被自动信号盖章成了「有用」，")
    print("    直接进训练集就是在教模型编造听起来专业的错误结论。")

    print(f"\n  **假阴性**（有用但代码没变）：{cal['false_negatives']}")
    for cid in cal["false_negatives"]:
        c = next(x for x in comments if x["comment_id"] == cid)
        print(f"    {cid} [{c['type']}] 「{c['body'][:56]}…」")
    print(
        "  → 这条评论是对的，作者当时没改；三周后它变成了一个真 bug"
        "（见 signals.py 的 SZZ 部分）。"
    )
    print("    **采纳信号会系统性低估「作者当时不认可但其实正确」的评论。**")

    print("\n  ⭐ 结论：采纳信号是**有偏的 proxy**，不能直接当 label 用。")
    print("     正确用法是「大规模弱标签 + 小规模人工校准」——")
    print("     BitsAI-CR 每天抽 ≤10% 人工标注、每周汇总，就是在做这件事。")
```




## pairs.py

```python
"""正负样本怎么造 —— 以及**三个会毁掉数据集的陷阱**。

code review 的正负样本比 math 难，因为「负」有五种完全不同的含义：

    ① 这条评论是**错的**（事实错误）        → 训练目标：别编
    ② 这条评论是**对的但没价值**（nit）      → 训练目标：别啰嗦
    ③ 这条评论**位置指错了**                 → 训练目标：定位要准
    ④ 这段代码**没有任何评论**               → ⚠️ **这不是负样本**
    ⑤ 这条评论**重复了别人已经说过的**       → 训练目标：别重复

**把 ④ 当负样本是这个领域最经典的错误。** 没人评论只说明没人看，
不说明代码没问题 —— 这是 positive-unlabeled，不是二分类。

    python pairs.py
"""

from __future__ import annotations

import json
import random
from collections import Counter

import gate
import signals
import toyreview

RNG = random.Random(0)


# ─────────────────────────────────────────── 三类正样本
def positives(comments: list, szz_pos: list) -> list:
    """按**证据强度**分层，不是一视同仁。训练时可以按层加权。"""
    out = []
    for c in comments:
        if c["signal"]["resolved"]:
            out.append(
                {
                    "kind": "resolved_comment",
                    "evidence": "weak",
                    "why": f"作者在 {c['signal']['by']} 改了这一行",
                    "path": c["path"],
                    "line": c["line"],
                    "text": c["body"],
                    "_gt_useful": c["_gt_useful"],
                }
            )
    for p in szz_pos:
        out.append(
            {
                "kind": "szz_verified_defect",
                "evidence": "strong",
                "why": p["evidence"],
                "path": p["path"],
                "line": p["line"],
                "text": p["defect_description"],
                "_gt_useful": 1,
            }
        )
    return out


# ─────────────────────────────────────────── 四类真负样本 + 一个陷阱
def negatives(comments: list, all_lines: dict) -> dict:
    """返回 {类别: [样本]}。注意 `unreviewed_line` 是**陷阱组**，默认不进训练集。"""
    neg = {
        "factually_wrong": [],
        "low_value_nit": [],
        "duplicate": [],
        "misplaced": [],
        "unreviewed_line": [],
    }

    kept, dups = gate.dedup_comments(comments, thr=0.10)
    dup_ids = {d["comment_id"] for d in dups}

    for c in comments:
        t = gate.classify(c)
        item = {
            "path": c["path"],
            "line": c["line"],
            "text": c["body"],
            "comment_id": c["comment_id"],
            "_gt_useful": c["_gt_useful"],
        }
        if c["comment_id"] in dup_ids:
            neg["duplicate"].append(item)
        elif t in ("nit_style", "praise", "question", "bot"):
            neg["low_value_nit"].append(item)
        elif not c["_gt_useful"]:
            # 真实场景里这一类要靠人工/强模型判定「事实是否成立」
            neg["factually_wrong"].append(item)

    # ③ 位置指错：把一条真评论的行号随机挪开 —— **廉价且高价值的合成负例**
    for c in [x for x in comments if x["_gt_useful"]][:3]:
        n = len(all_lines.get(c["path"], []))
        wrong = RNG.choice([l for l in range(1, n + 1) if abs(l - c["line"]) > 4])
        neg["misplaced"].append(
            {
                "path": c["path"],
                "line": wrong,
                "text": c["body"],
                "comment_id": c["comment_id"] + "-mis",
                "_gt_useful": 0,
            }
        )

    # ④ 陷阱组：没被评论过的行
    for path, lines in all_lines.items():
        for i, code in enumerate(lines, 1):
            if code.strip() and not any(
                c["path"] == path and c["line"] == i for c in comments
            ):
                neg["unreviewed_line"].append(
                    {"path": path, "line": i, "text": None, "code": code.strip()}
                )
    return neg


# ─────────────────────────────────────────── 偏好对
def preference_pairs(pos: list, neg: dict, per_positive: int = 2) -> list:
    """给 DPO / reward model 用的 (chosen, rejected)。

    **关键：配对要在同一个 (文件, 行) 上下文里**。
    如果 chosen 来自 auth.py、rejected 来自 orders.py，模型学到的可能是
    「auth 相关的评论更好」这种和质量无关的捷径 —— 这是最常见的 pair 泄漏。
    """
    pool = (
        neg["factually_wrong"]
        + neg["low_value_nit"]
        + neg["duplicate"]
        + neg["misplaced"]
    )
    pairs = []
    for p in pos:
        same_file = [n for n in pool if n["path"] == p["path"]] or pool
        for n in RNG.sample(same_file, min(per_positive, len(same_file))):
            pairs.append(
                {
                    "context": {"path": p["path"], "line": p["line"]},
                    "chosen": p["text"],
                    "rejected": n["text"],
                    "chosen_kind": p["kind"],
                    "rejected_kind": _kind_of(n, neg),
                    "same_file": p["path"] == n["path"],
                }
            )
    return pairs


def _kind_of(item, neg):
    for k, v in neg.items():
        if item in v:
            return k
    return "?"


if __name__ == "__main__":
    built = toyreview.build()
    root, gt = built["root"], built["gt"]
    comments = signals.annotate(root, built["comments"])
    szz_pos = signals.szz_positives(root, gt["commits"]["orders_bugfix"])

    all_lines = {}
    for path in ("shop/orders.py", "shop/auth.py"):
        sha = gt["commits"]["orders_v1" if "orders" in path else "auth_v1"]
        all_lines[path] = toyreview.sh(
            f"git show {sha}:{path}", root
        ).stdout.splitlines()

    pos = positives(comments, szz_pos)
    neg = negatives(comments, all_lines)

    print("═══ 正样本（按证据强度分层）═══\n")
    for k, v in Counter(p["kind"] for p in pos).items():
        ev = next(p["evidence"] for p in pos if p["kind"] == k)
        bad = sum(1 for p in pos if p["kind"] == k and not p["_gt_useful"])
        print(f"  {k:<24} {v:>2} 条  证据={ev:<7} 其中实际没用的 {bad} 条")
    print("\n  ⭐ **强弱证据不能等权**：SZZ 的正样本由后来真实发生的修复所证明；")
    print("     采纳信号的正样本里混着 3 条假阳性（见 gate.py）。")
    print("     实践：强证据权重 1.0，弱证据 0.3–0.5，或者只用强证据训 reward model。")

    print("\n═══ 负样本（四真一假）═══\n")
    for k, v in neg.items():
        flag = "  ⚠️ 陷阱组，默认不进训练集" if k == "unreviewed_line" else ""
        print(f"  {k:<20} {len(v):>3} 条{flag}")
    print(
        "\n  ⚠️ `unreviewed_line` 有 {} 条 —— 如果把它们当负样本，"
        "负例会瞬间淹没正例\n     （{}:{} 的比例），而且**它们里面有真问题**：".format(
            len(neg["unreviewed_line"]), len(neg["unreviewed_line"]), len(pos)
        )
    )
    # 证明：cm03 指出的那行确实有 bug，但当时没人再评论，SZZ 后来证实了
    bug_line = szz_pos[0]
    print(f"     例：{bug_line['path']}:{bug_line['line']} 当时没有有效评论，")
    print(f"     三周后被 fix 掉了 —— 它**本该是正样本**。")
    print("     → 「没有评论」是 positive-unlabeled，不是负类。")

    print("\n═══ 偏好对 ═══\n")
    pairs = preference_pairs(pos, neg)
    print(
        f"  生成 {len(pairs)} 对，同文件配对比例 "
        f"{sum(p['same_file'] for p in pairs) / len(pairs):.0%}"
    )
    print("\n  样例：")
    ex = next(p for p in pairs if p["rejected_kind"] == "factually_wrong")
    print(json.dumps(ex, ensure_ascii=False, indent=2)[:600])
    print("\n  配对类型分布：")
    for k, v in Counter(p["rejected_kind"] for p in pairs).most_common():
        print(f"    rejected = {k:<20} {v}")
```




## reward.py

```python
"""Reward 设计：**分层 + 精度优先 + 防 hack**。

和 math/SWE 的 RL 最大的不同：

    math：reward = 答案对不对         → 对称，找不到只是没得分
    SWE ：reward = 测试过不过         → 对称
    CR  ：**误报会主动造成伤害**       → **不对称**

一条错误的 review 评论不是「没得分」，它消耗 reviewer 的信任。
ByteDance 的数据：只有 30% 的 review 会被立刻看；一旦机器人开始说废话，
开发者就整体屏蔽它 —— **一次误报的代价远大于一次漏报**。

所以 reward 的第一原则是**精度优先**，而不是 F1 最大化。
BitsAI-CR 因此上了两段式：RuleChecker 先找，**ReviewFilter 再砍**。

    python reward.py
"""

from __future__ import annotations

import re

import numpy as np


# ══════════════════════════════════════════ 分层 reward
def r1_deterministic(comment: dict, ctx: dict) -> dict:
    """**第一层：确定性硬闸门**。免费、不漂移、不需要校准。

    能被静态分析/编译器/规则确定的东西，就不要交给模型判断：
      * 评论指向的行号存在吗？（越界 = 直接判 0）
      * 评论声称的 API/符号在这个版本里存在吗？（防「过期引用」）
      * 有没有对应的 linter/SAST 规则命中？（命中 = 强证据）
    """
    reasons = []
    if not (1 <= comment["line"] <= ctx["n_lines"]):
        return {"score": 0.0, "hard_fail": True, "reasons": ["行号越界"]}
    code = ctx["lines"][comment["line"] - 1]
    for sym in re.findall(r"`([A-Za-z_][\w.]*)`", comment["body"]):
        if sym not in ctx["source"]:
            reasons.append(f"引用了不存在的符号 `{sym}` → 疑似过期/幻觉")
            return {"score": 0.0, "hard_fail": True, "reasons": reasons}
    hit = any(rule in code for rule in ctx.get("sast_patterns", []))
    if hit:
        reasons.append("命中静态分析规则（强证据）")
    return {"score": 1.0 if hit else 0.5, "hard_fail": False, "reasons": reasons}


def r2_evidence(comment: dict, ctx: dict) -> dict:
    """**第二层：来自历史的证据**（本 lab 前面算出来的两个信号）。

    强证据（SZZ 证实这一行后来真的被 fix 了）> 弱证据（作者改了这一行）。
    """
    if comment.get("szz_confirmed"):
        return {"score": 1.0, "kind": "strong", "why": "后来真的被 bug-fix 修了"}
    if comment.get("resolved"):
        return {"score": 0.5, "kind": "weak", "why": "作者改了这一行（有 30% 假阳性）"}
    return {"score": 0.0, "kind": "none", "why": "无历史证据"}


def r3_judge(comment: dict, ctx: dict, judge_precision: float = 0.77) -> dict:
    """**第三层：LLM judge**。最贵、最会漂、**必须用人工标注校准**。

    BitsAI-CR 的一个反直觉发现值得抄（他们比了三种推理格式）：

        Direct Conclusion   （只出结论）        1.7s    63.27%
        Reasoning-First     （先推理后结论）    31.0s   65.80%   ← 慢 18 倍只多 2.5 个点
        Conclusion-First    （先结论后理由）    1.7s    **77.09%**  ← 选它

    **先给结论再给理由，比先推理再给结论精度更高而且快 18 倍。**
    一个可能的解释：先写结论迫使模型基于证据表态，而不是被自己
    生成的推理链带跑（推理链会为一个不成立的结论找补）。
    """
    return {
        "score": judge_precision,
        "cost": 1.0,
        "note": "分数要用人工标注校准过才可信",
    }


def total_reward(
    comment: dict, ctx: dict, w=(0.3, 0.5, 0.2), fp_penalty: float = 3.0
) -> dict:
    """**硬闸门在前，加权在后，误报单独重罚。**

    `fp_penalty=3.0` 是这套设计的核心：一次误报抵三次正确。
    这个数不是拍的 —— 它应该由「一次误报让用户少看多少条后续评论」估出来。
    """
    r1 = r1_deterministic(comment, ctx)
    if r1["hard_fail"]:
        return {"reward": -fp_penalty, "breakdown": {"r1": r1}, "gated": True}
    r2, r3 = r2_evidence(comment, ctx), r3_judge(comment, ctx)
    base = w[0] * r1["score"] + w[1] * r2["score"] + w[2] * r3["score"]
    verbosity = max(0, len(comment["body"]) - 400) / 400 * 0.1  # 啰嗦轻罚
    return {
        "reward": round(base - verbosity, 3),
        "gated": False,
        "breakdown": {"r1": r1, "r2": r2, "r3": r3, "verbosity": -verbosity},
    }


# ══════════════════════════════════════════ 精度优先：两段式
def two_stage(
    checker_recall: float = 0.62,
    checker_precision: float = 0.28,
    filter_thresholds=None,
    trust_decay: float = 0.75,
):
    """模拟 RuleChecker → ReviewFilter 两段式，扫 filter 阈值。

    参数取自 BitsAI-CR 上线初期的真实数字：
    RuleChecker 精度 27.9%（后来优化到 62.6%），ReviewFilter 把它拉到 75.0%。

    **要看的不是 F1，是「用户还愿不愿意读」。**
    这里用一个简单的信任模型：一个 PR 上误报越多，用户读后续评论的概率越低。
    """
    thresholds = filter_thresholds or [0.0, 0.3, 0.5, 0.7, 0.85, 0.95]
    n_real = 3.0  # 假设每个 PR 平均 3 个真问题
    tp0 = n_real * checker_recall
    fp0 = tp0 * (1 - checker_precision) / max(checker_precision, 1e-9)
    rows = []
    for t in thresholds:
        # filter 阈值越高，砍掉的误报越多，但也会误伤真问题
        keep_fp = fp0 * (1 - t) ** 1.6
        keep_tp = tp0 * (1 - t) ** 0.35
        prec = keep_tp / max(keep_tp + keep_fp, 1e-9)
        # 信任模型：每多一条误报，用户继续读后续评论的概率乘 trust_decay
        trust = trust_decay**keep_fp
        adopted = keep_tp * trust  # 实际被采纳的真问题数
        rows.append(
            {
                "thr": t,
                "comments_per_pr": keep_tp + keep_fp,
                "precision": prec,
                "recall": keep_tp / n_real,
                "f1": 2
                * prec
                * (keep_tp / n_real)
                / max(prec + keep_tp / n_real, 1e-9),
                "trust": trust,
                "adopted_per_pr": adopted,
            }
        )
    return rows


# ══════════════════════════════════════════ 防 hack
def hack_signals(comments: list) -> dict:
    """reward hacking 在 code review 上的三个典型形态。"""
    n = max(1, len(comments))
    lens = [len(c["body"]) for c in comments]
    hedged = sum(
        1
        for c in comments
        if re.search(
            r"\b(might|may|could|consider|possibly|perhaps)\b", c["body"], re.I
        )
    )
    generic = sum(
        1
        for c in comments
        if re.search(
            r"\b(add (a )?(unit )?tests?|add error handling|add (a )?docstring|"
            r"consider refactoring)\b",
            c["body"],
            re.I,
        )
    )
    per_line = {}
    for c in comments:
        per_line.setdefault((c["path"], c["line"]), 0)
        per_line[(c["path"], c["line"])] += 1
    return {
        "① 模糊化（用 might/could 规避被判错）": hedged / n,
        "② 万能话术（『加个测试』适用于任何代码）": generic / n,
        "③ 散弹枪（同一行堆多条以提高命中率）": sum(v - 1 for v in per_line.values())
        / n,
        "平均长度": float(np.mean(lens)),
    }


if __name__ == "__main__":
    import gate, signals, toyreview

    built = toyreview.build()
    root, gt = built["root"], built["gt"]
    comments = signals.annotate(root, built["comments"])
    szz = {
        (p["path"], p["line"])
        for p in signals.szz_positives(root, gt["commits"]["orders_bugfix"])
    }

    src = toyreview.sh(f"git show {gt['commits']['auth_v1']}:shop/auth.py", root).stdout
    ctx = {
        "source": src,
        "lines": src.splitlines(),
        "n_lines": len(src.splitlines()),
        "sast_patterns": ["md5(", '" + ', "SELECT"],
    }

    print("═══ 分层 reward（shop/auth.py 上的评论）═══\n")
    for c in [x for x in comments if x["path"] == "shop/auth.py"][:6]:
        c2 = {
            **c,
            "resolved": c["signal"]["resolved"],
            "szz_confirmed": (c["path"], c["line"]) in szz,
        }
        r = total_reward(c2, ctx)
        tag = "⛔ 硬闸门" if r["gated"] else f"{r['reward']:+.3f}"
        print(f"  {c['comment_id']} [{c['type']:<15}] {tag:<12} 「{c['body'][:44]}…」")
        for k in ("r1", "r2"):
            if k in r["breakdown"]:
                b = r["breakdown"][k]
                extra = b.get("why") or "；".join(b.get("reasons", [])) or "—"
                print(f"        {k}={b['score']:.2f}  {extra}")

    print("\n═══ 精度优先：为什么不能最大化 F1 ⭐ ═══\n")
    print(
        "  {:<6} {:>8} {:>9} {:>8} {:>7} {:>7} {:>12}".format(
            "阈值", "条/PR", "precision", "recall", "F1", "信任", "**实际采纳**"
        )
    )
    rows = two_stage()
    for r in rows:
        print(
            "  {:<6.2f} {:>8.2f} {:>8.0%} {:>8.0%} {:>7.2f} {:>7.0%} {:>12.2f}".format(
                r["thr"],
                r["comments_per_pr"],
                r["precision"],
                r["recall"],
                r["f1"],
                r["trust"],
                r["adopted_per_pr"],
            )
        )
    best_f1 = max(rows, key=lambda r: r["f1"])
    best_ad = max(rows, key=lambda r: r["adopted_per_pr"])
    print(
        f"\n  这组参数下 F1 最优和采纳最优**都在 {best_f1['thr']:.2f}** —— 它们没有分离。"
    )
    print("  ⚠️ 我原本想在这里演示「F1 最优 ≠ 产品最优」，但数据不支持这个说法。")
    print("     正确的问题不是「它们是否分离」，而是**「误报多贵时才分离」**：\n")

    fine = [i / 40 for i in range(0, 40)]
    print(
        "  {:<12} {:>12} {:>14} {:>10}".format(
            "每条误报的信任衰减", "F1 最优阈值", "实际采纳最优阈值", "差距"
        )
    )
    for decay in (0.95, 0.85, 0.75, 0.60, 0.45):
        rs = two_stage(filter_thresholds=fine, trust_decay=decay)
        tf = max(rs, key=lambda r: r["f1"])["thr"]
        ta = max(rs, key=lambda r: r["adopted_per_pr"])["thr"]
        print(
            "  {:<12.2f} {:>12.3f} {:>14.3f} {:>10.3f}".format(decay, tf, ta, ta - tf)
        )
    print("\n  → **差距随误报代价单调变化，而 F1 最优阈值岿然不动（永远 0.675）。**")
    print("     衰减 0.95（误报几乎无害）→ 产品最优 0.075，**比 F1 宽松 0.6**")
    print("       （既然误报不疼，就该把召回拉满）")
    print("     衰减 0.75 → 恰好重合（这只是巧合，不是规律）")
    print("     衰减 0.45（一条误报让用户少读一半）→ 产品最优 0.825，比 F1 更严")
    print("  ⭐ **F1 根本不知道一次误报值多少钱** —— 它在任何代价下都给同一个答案。")
    print(
        "  ⭐ 所以要问的不是「用不用 F1」，是**「一条误报到底让用户少看了多少条」** ——"
    )
    print("     这个数要从线上量（BitsAI-CR 的 Outdated Rate 就是干这个的），")
    print("     量出来之后，阈值不是调参调出来的，是**算出来的**。")
    print("     顺带解释了他们为什么把 ReviewFilter 做成独立一段：")
    print("     它的阈值要按产品目标单独定，不该和 RuleChecker 的召回耦合。")

    print("\n═══ reward hacking 监控 ═══\n")
    for k, v in hack_signals(comments).items():
        print(f"  {k:<38} {v:.2f}")
    print("\n  这三个指标要**按周画趋势**。任何一个开始上涨，")
    print("  就说明模型在学「怎么让 grader 满意」而不是「怎么发现问题」。")
    print("  配套的硬护栏：每条评论必须给出**可定位的行号 + 可证伪的断言**，")
    print("  『考虑加个测试』这种既不可定位也不可证伪的话直接在 r1 层砍掉。")
```




## signals.py

```python
"""**制造可验证性**：从 git 历史里算出两种自动 ground truth。

code review 没有测试可跑。所以第一件事不是训模型，是**找到一个能自动算、
且和「有没有用」相关的信号**。业界收敛到的两个：

  ① **采纳信号**（BitsAI-CR 叫 Outdated Rate，Atlassian 叫 Code Resolution Rate）
     评论指向的代码行，在后续 commit 里被改了吗？
     · ByteDance：Go 语言上做到 26.7%；**人类 reviewer 的基线是 35–46%**
     · Atlassian：CRR 做到 40–45%，**人类约 45%**
     两家独立地选了同一个信号 —— 因为它是**唯一能在生产里零成本、全量拿到的**。

  ② **SZZ**：bug-fix commit → git blame 被修的行 → 找到**引入 bug 的 commit**
     产出 `(历史版本的代码, 这一行确实有缺陷)` —— 一条**可验证的正样本**。
     ⚠️ 它有硬限制，见 `szz()` 的 docstring。

    python signals.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import toyreview
from toyreview import sh

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


# ─────────────────────────────────────────── ① 采纳信号
def changed_old_lines(root: Path, a: str, b: str, path: str) -> set:
    """`git diff a..b -- path` 中**旧文件（a 版本）里被删改的行号集合**。

    关键在于读 hunk 头 `@@ -old_start,old_len +new_start,new_len @@` 的**左边**：
    右边是新文件的行号，用错了就会把采纳信号算歪。
    """
    out = sh(f"git diff -U0 {a} {b} -- {path}", root, check=False).stdout
    touched = set()
    for line in out.splitlines():
        m = HUNK.match(line)
        if m:
            start, ln = int(m.group(1)), int(m.group(2) or 1)
            touched |= set(range(start, start + max(ln, 1)))
            if ln == 0:  # 纯新增：把插入点前后各算一行
                touched |= {start, start + 1}
    return touched


def next_commit_touching(root: Path, after: str, path: str):
    """`after` 之后第一个改动了 `path` 的 commit。"""
    out = sh(
        f"git log --reverse --format=%H {after}..HEAD -- {path}", root, check=False
    ).stdout.split()
    return out[0] if out else None


def resolution_signal(root: Path, comment: dict, window_commits: int = 3) -> dict:
    """这条评论指向的行，之后被改了吗？

    `window_commits` 是时间窗 —— BitsAI-CR 用的是**一周**。
    窗口太长会把无关的重构算成「采纳」，太短会漏掉慢反应的作者。
    **这是个必须扫的超参，不是常数。**
    """
    cur, seen = comment["commit"], 0
    while seen < window_commits:
        nxt = next_commit_touching(root, cur, comment["path"])
        if not nxt:
            break
        touched = changed_old_lines(root, cur, nxt, comment["path"])
        if comment["line"] in touched:
            return {"resolved": 1, "by": nxt[:7], "n_hops": seen + 1}
        cur, seen = nxt, seen + 1
    return {"resolved": 0, "by": None, "n_hops": seen}


# ─────────────────────────────────────────── ② SZZ
def szz(root: Path, fix_commit: str) -> list:
    """给一个 bug-fix commit，回溯**引入 bug 的 commit**。

    做法：取 fix 删改掉的行 → 在 fix 的父提交上 `git blame` 这些行 →
    最后碰过它们的 commit 就是嫌疑人。

    ⚠️ **诚实说清 SZZ 的边界**（这是学界反复量化过的）：
      * **ghost commit**：fix 只新增不删改 → blame 无从下手。
        Linux kernel 上占 **17.47%**
      * **跨文件**：bug 的成因在别的文件里，占 **7.20%**
      * 综合起来 **超过 40% 的 case 光靠 blame 解决不了**
        （28% 需要往上翻更多历史，14% 完全 blameless）
      * 纯格式化/重构 commit 会被误认成 inducing —— 要用
        「忽略空白改动」的 blame（`-w`）+ 重构检测来缓解

    所以 SZZ 给的是**高精度但低召回**的正样本。它适合当种子，不适合当全集。
    """
    parent = sh(f"git rev-parse {fix_commit}~1", root).stdout.strip()
    files = sh(f"git diff --name-only {parent} {fix_commit}", root).stdout.split()
    out = []
    for path in files:
        old_lines = sorted(changed_old_lines(root, parent, fix_commit, path))
        if not old_lines:
            out.append({"path": path, "ghost": True, "inducing": []})
            continue
        inducing = {}
        for ln in old_lines:
            # -w 忽略纯空白改动，避免把格式化 commit 当成 bug 的来源
            b = sh(
                f"git blame -w -L {ln},{ln} --porcelain {parent} -- {path}",
                root,
                check=False,
            ).stdout
            if b:
                sha = b.split()[0]
                inducing.setdefault(sha, []).append(ln)
        out.append(
            {
                "path": path,
                "ghost": False,
                "inducing": [{"commit": s, "lines": ls} for s, ls in inducing.items()],
            }
        )
    return out


def szz_positives(root: Path, fix_commit: str) -> list:
    """把 SZZ 的结果变成**训练用的正样本**：
    「在 inducing commit 的这个版本上，这一行有缺陷，缺陷描述来自 fix 的 message」。

    这是 code review 数据里**唯一一类真正可验证的正样本** ——
    因为它由后来真实发生的修复所证明，不依赖任何人的主观判断。
    """
    msg = sh(f"git log -1 --format=%s {fix_commit}", root).stdout.strip()
    pos = []
    for f in szz(root, fix_commit):
        for ind in f["inducing"]:
            snippet = sh(
                f"git show {ind['commit']}:{f['path']}", root, check=False
            ).stdout.splitlines()
            for ln in ind["lines"]:
                pos.append(
                    {
                        "kind": "szz_verified_defect",
                        "commit": ind["commit"],
                        "path": f["path"],
                        "line": ln,
                        "code": snippet[ln - 1].strip() if ln <= len(snippet) else "",
                        "defect_description": msg,
                        "evidence": f"fixed in {fix_commit[:7]}",
                    }
                )
    return pos


# ─────────────────────────────────────────── 汇总
def annotate(root: Path, comments: list) -> list:
    for c in comments:
        c["signal"] = resolution_signal(root, c)
    return comments


if __name__ == "__main__":
    built = toyreview.build()
    root, comments, gt = built["root"], built["comments"], built["gt"]

    print("═══ ① 采纳信号（真的用 git diff 算的）═══\n")
    annotate(root, comments)
    print(
        "{:<6} {:<16} {:<5} {:<9} {:>8} {:>8}".format(
            "id", "type", "line", "resolved", "真值采纳", "真值有用"
        )
    )
    for c in comments:
        print(
            "{:<6} {:<16} {:<5} {:<9} {:>8} {:>8}".format(
                c["comment_id"],
                c["type"],
                c["line"],
                "✅ " + (c["signal"]["by"] or "") if c["signal"]["resolved"] else "❌",
                c["_gt_addressed"],
                c["_gt_useful"],
            )
        )

    n = len(comments)
    res = sum(c["signal"]["resolved"] for c in comments)
    agree = sum(c["signal"]["resolved"] == c["_gt_addressed"] for c in comments)
    print(f"\n采纳率（Outdated Rate 类比）= {res}/{n} = {res / n:.0%}")
    print(f"和真值一致 {agree}/{n} = {agree / n:.0%}")
    print("参考：ByteDance Go 26.7%（人类 35–46%）；Atlassian CRR 40–45%（人类 ~45%）")

    print("\n═══ ② SZZ（真的用 git blame 回溯的）═══\n")
    fix = gt["commits"]["orders_bugfix"]
    print(
        f"bug-fix commit：{fix[:7]}  "
        f"{sh(f'git log -1 --format=%s {fix}', root).stdout.strip()}"
    )
    for f in szz(root, fix):
        for ind in f["inducing"]:
            exp = gt["szz_expected"]["inducing_commit"]
            ok = "✅ 命中期望" if ind["commit"].startswith(exp[:7]) else "⚠️ 与期望不符"
            print(
                f"  {f['path']}  行 {ind['lines']} ← 由 {ind['commit'][:7]} 引入  {ok}"
            )

    print("\n可验证正样本：")
    for p in szz_positives(root, fix):
        print(f"  {p['path']}:{p['line']}  `{p['code'][:52]}`")
        print(f"    缺陷：{p['defect_description'][:70]}")
        print(f"    证据：{p['evidence']}")
```




## test_cr_data.py

```python
"""锁住 code review 数据 pipeline 的关键不变量。`pytest test_cr_data.py -q`"""

from __future__ import annotations

import pytest

import gate
import pairs
import reward
import signals
import toyreview

BUILT = toyreview.build()
ROOT, GT = BUILT["root"], BUILT["gt"]
COMMENTS = signals.annotate(ROOT, BUILT["comments"])
SZZ_POS = signals.szz_positives(ROOT, GT["commits"]["orders_bugfix"])


# ───────────────────────────── 信号
def test_szz_finds_the_right_inducing_commit():
    """SZZ 必须回溯到真正引入 bug 的那个 commit。"""
    res = signals.szz(ROOT, GT["commits"]["orders_bugfix"])
    inducing = {i["commit"] for f in res for i in f["inducing"]}
    assert GT["szz_expected"]["inducing_commit"] in inducing


def test_szz_positives_carry_code_and_evidence():
    assert SZZ_POS
    for p in SZZ_POS:
        assert p["code"] and p["defect_description"] and p["evidence"]


def test_resolution_uses_old_line_numbers():
    """hunk 头左边是旧文件行号。读成右边（新文件）会把采纳信号算歪。"""
    a, b = GT["commits"]["orders_v1"], GT["commits"]["orders_review"]
    touched = signals.changed_old_lines(ROOT, a, b, "shop/orders.py")
    assert 3 in touched  # DISCOUNT 那行确实被改了
    assert 1 not in touched  # import json 没被改


def test_resolution_signal_is_computed_not_hardcoded():
    resolved = [c for c in COMMENTS if c["signal"]["resolved"]]
    assert 0 < len(resolved) < len(COMMENTS)
    for c in resolved:
        assert c["signal"]["by"]


# ───────────────────────────── 质量把关
def test_bot_detection():
    assert gate.is_bot("codecov[bot]") and gate.is_bot("dependabot")
    assert not gate.is_bot("alice")


def test_gate_raises_useful_ratio():
    """过滤的唯一目的：提高有价值评论的占比。不提高就是白做。"""
    before = sum(c["_gt_useful"] for c in COMMENTS) / len(COMMENTS)
    final = gate.gate(COMMENTS)["final"]
    after = sum(c["_gt_useful"] for c in final) / len(final)
    assert after > before + 0.2


def test_lexical_dedup_misses_paraphrases():
    """诚实记录：词袋 Jaccard 在 0.35 阈值下**一条改写都抓不到**。
    cm18 是 cm11 的改写、cm19 是 cm01 的改写 —— 语义去重必须上 embedding。"""
    sub = [c for c in COMMENTS if gate.classify(c) == "substantive"]
    _, at35 = gate.dedup_comments(sub, 0.35)
    _, at10 = gate.dedup_comments(sub, 0.10)
    assert len(at35) == 0
    assert {d["comment_id"] for d in at10} >= {"cm18", "cm19"}


def test_resolution_signal_has_false_positives():
    """**核心主张**：采纳信号是有偏 proxy，不能直接当 label。"""
    cal = gate.calibrate(COMMENTS)
    assert cal["false_positives"], "必须能演示出假阳性"
    assert cal["precision"] < 0.85, "精度不该高到让人误以为它可以直接用"


def test_wrong_comment_gets_credited_by_resolution_signal():
    """最危险的那条：cm17 事实错误，却因为落在被改的行上而被记成采纳。"""
    cm17 = next(c for c in COMMENTS if c["comment_id"] == "cm17")
    assert cm17["_gt_useful"] == 0
    assert cm17["signal"]["resolved"] == 1


def test_correct_but_unaddressed_comment_is_missed():
    """cm03 是对的、当时没被采纳，三周后变成真 bug —— 假阴性。"""
    cm03 = next(c for c in COMMENTS if c["comment_id"] == "cm03")
    assert cm03["_gt_useful"] == 1 and cm03["signal"]["resolved"] == 0
    assert any(p["line"] in (21, 22, 23) for p in SZZ_POS)


# ───────────────────────────── 正负样本
def _neg():
    all_lines = {}
    for path, key in (("shop/orders.py", "orders_v1"), ("shop/auth.py", "auth_v1")):
        all_lines[path] = toyreview.sh(
            f"git show {GT['commits'][key]}:{path}", ROOT
        ).stdout.splitlines()
    return pairs.negatives(COMMENTS, all_lines), all_lines


def test_positives_are_stratified_by_evidence_strength():
    pos = pairs.positives(COMMENTS, SZZ_POS)
    kinds = {p["evidence"] for p in pos}
    assert kinds == {"weak", "strong"}


def test_unreviewed_lines_are_kept_separate():
    """**这个领域最经典的错误**：把「没人评论的行」当负样本。
    没人评论只说明没人看 —— 这是 positive-unlabeled，不是二分类。"""
    neg, _ = _neg()
    assert neg["unreviewed_line"]
    pool = (
        neg["factually_wrong"]
        + neg["low_value_nit"]
        + neg["duplicate"]
        + neg["misplaced"]
    )
    assert not any(n in pool for n in neg["unreviewed_line"])


def test_an_unreviewed_line_actually_contained_a_real_bug():
    """证明上一条不是洁癖：未被评论的行里**确实有**后来被修的真 bug。"""
    neg, _ = _neg()
    unrev = {(n["path"], n["line"]) for n in neg["unreviewed_line"]}
    assert any((p["path"], p["line"]) in unrev for p in SZZ_POS)


def test_pairs_are_matched_within_the_same_file():
    """chosen 和 rejected 跨文件配对 = 模型可以靠文件名走捷径。"""
    neg, _ = _neg()
    ps = pairs.preference_pairs(pairs.positives(COMMENTS, SZZ_POS), neg)
    assert ps and all(p["same_file"] for p in ps)


def test_misplaced_negatives_are_far_from_the_original_line():
    neg, _ = _neg()
    for m in neg["misplaced"]:
        orig = next(
            c
            for c in COMMENTS
            if c["comment_id"] == m["comment_id"].replace("-mis", "")
        )
        assert abs(m["line"] - orig["line"]) > 4


# ───────────────────────────── reward
def _ctx():
    src = toyreview.sh(f"git show {GT['commits']['auth_v1']}:shop/auth.py", ROOT).stdout
    return {
        "source": src,
        "lines": src.splitlines(),
        "n_lines": len(src.splitlines()),
        "sast_patterns": ["md5(", "SELECT"],
    }


def test_hard_gate_rejects_out_of_range_line():
    r = reward.total_reward({"line": 999, "body": "x"}, _ctx())
    assert r["gated"] and r["reward"] < 0


def test_hard_gate_rejects_hallucinated_symbol():
    """评论引用了代码里不存在的符号 → 过期引用或幻觉，直接砍。"""
    r = reward.total_reward(
        {"line": 4, "body": "the `read_orders` helper is deprecated"}, _ctx()
    )
    assert r["gated"]


def test_szz_evidence_outranks_resolution_evidence():
    c = {"line": 4, "body": "md5 is broken"}
    strong = reward.total_reward({**c, "szz_confirmed": True}, _ctx())["reward"]
    weak = reward.total_reward({**c, "resolved": True}, _ctx())["reward"]
    none = reward.total_reward(c, _ctx())["reward"]
    assert strong > weak > none


def test_f1_optimum_ignores_false_positive_cost():
    """**核心主张**：F1 最优阈值不随误报代价变化，产品最优会变。"""
    fine = [i / 40 for i in range(40)]
    f1_opts, ad_opts = [], []
    for d in (0.95, 0.75, 0.45):
        rs = reward.two_stage(filter_thresholds=fine, trust_decay=d)
        f1_opts.append(max(rs, key=lambda r: r["f1"])["thr"])
        ad_opts.append(max(rs, key=lambda r: r["adopted_per_pr"])["thr"])
    assert len(set(f1_opts)) == 1, "F1 最优不该随误报代价变"
    assert ad_opts == sorted(ad_opts), "误报越贵，产品最优该越保守"
    assert ad_opts[0] < f1_opts[0] < ad_opts[-1], "两端要跨过 F1 的最优点"


def test_hack_signals_are_all_computed():
    h = reward.hack_signals(COMMENTS)
    assert set(h) and all(isinstance(v, float) for v in h.values())
```




## toyreview.py

```python
"""造 code review 的训练语料：git 历史 + review 评论 + **可计算的采纳信号**。

和 SWE agent 数据最大的不同：**这里没有测试可以跑。**
「这条评论有没有用」没有执行 oracle。所以造数据的核心工作变成了
**制造可验证性** —— 从历史里挖出两种能自动计算的 ground truth：

  ① **采纳信号（resolution / outdated）**
     评论指向的代码行，在后续 commit 里被改了吗？
     改了 → 作者认可了这条评论。
     ByteDance BitsAI-CR 叫 Outdated Rate，Atlassian 叫 Code Resolution Rate ——
     **两家独立地收敛到了同一个信号**，这不是巧合。

  ② **SZZ：真实缺陷的位置**
     一个 bug-fix commit 修了哪几行 → git blame 那几行 → 找到**引入 bug 的 commit**。
     于是你得到 `(某个历史版本的代码, 这一行确实有缺陷)` —— 一条**可验证的正样本**。

本文件产出（全部落到 /tmp/cr_toyrepo）：
  * 一个 git 仓库：feature commit 引入缺陷 → review → 部分被采纳的 follow-up → 后来的 bug-fix
  * `comments.jsonl`：42 条 review 评论，混着真信号和五类噪声
  * `groundtruth.json`：我知道正确答案，用来给 pipeline 写断言
"""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from pathlib import Path

DEFAULT = Path("/tmp/cr_toyrepo")

# 评论类型：前四类是 BitsAI-CR 的四个 review dimension，后五类是必须被过滤掉的噪声
SIGNAL_TYPES = ("code_defect", "security", "maintainability", "performance")
NOISE_TYPES = ("nit_style", "question", "praise", "bot", "obsolete")


def sh(cmd, cwd, check=True):
    return subprocess.run(
        cmd, cwd=str(cwd), shell=True, capture_output=True, text=True, check=check
    )


def _w(root: Path, rel: str, body: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip())


def _commit(root: Path, msg: str, date: str) -> str:
    sh("git add -A", root)
    sh(
        f'GIT_AUTHOR_DATE="{date}" GIT_COMMITTER_DATE="{date}" '
        f'git commit -q -m {msg!r}',
        root,
    )
    return sh("git rev-parse HEAD", root).stdout.strip()


# ─────────────────────────────────────────────────────────────
V1_ORDERS = '''
    import json

    DISCOUNT = 0.15

    def load_orders(path):
        with open(path) as f:
            return json.load(f)

    def total(order):
        s = 0
        for it in order["items"]:
            s += it["price"] * it["qty"]
        return s * (1 - DISCOUNT)

    def find_order(orders, oid):
        for o in orders:
            if o["id"] == oid:
                return o

    def apply_coupon(order, code):
        if code == "SAVE10":
            order["total"] = total(order) * 0.9
        return order["total"]
'''

# follow-up：作者采纳了两条评论（find_order 加了 None 处理、DISCOUNT 抽成参数）
V2_ORDERS = '''
    import json

    DEFAULT_DISCOUNT = 0.15

    def load_orders(path):
        with open(path) as f:
            return json.load(f)

    def total(order, discount=DEFAULT_DISCOUNT):
        s = 0
        for it in order["items"]:
            s += it["price"] * it["qty"]
        return s * (1 - discount)

    def find_order(orders, oid):
        for o in orders:
            if o["id"] == oid:
                return o
        raise KeyError(f"no order {oid}")

    def apply_coupon(order, code):
        if code == "SAVE10":
            order["total"] = total(order) * 0.9
        return order["total"]
'''

# 后来的 bug-fix：apply_coupon 在 code 不匹配时返回未设置的 key → KeyError
V3_ORDERS_FIX = '''
    import json

    DEFAULT_DISCOUNT = 0.15

    def load_orders(path):
        with open(path) as f:
            return json.load(f)

    def total(order, discount=DEFAULT_DISCOUNT):
        s = 0
        for it in order["items"]:
            s += it["price"] * it["qty"]
        return s * (1 - discount)

    def find_order(orders, oid):
        for o in orders:
            if o["id"] == oid:
                return o
        raise KeyError(f"no order {oid}")

    def apply_coupon(order, code):
        order.setdefault("total", total(order))
        if code == "SAVE10":
            order["total"] = total(order) * 0.9
        return order["total"]
'''

V1_AUTH = '''
    import hashlib

    def hash_pw(pw):
        return hashlib.md5(pw.encode()).hexdigest()

    def check(user, pw, db):
        row = db.execute("SELECT pw FROM users WHERE name = '" + user + "'")
        return row and row[0] == hash_pw(pw)
'''

V2_AUTH = '''
    import hashlib

    def hash_pw(pw, salt):
        return hashlib.sha256((salt + pw).encode()).hexdigest()

    def check(user, pw, db):
        row = db.execute("SELECT pw, salt FROM users WHERE name = ?", (user,))
        return bool(row) and row[0] == hash_pw(pw, row[1])
'''


def build(root: Path = DEFAULT) -> dict:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    sh("git init -q -b main", root)
    sh('git config user.email dev@x.io && git config user.name Dev', root)

    _w(root, "README.md", "# shop\n")
    c0 = _commit(root, "init", "2025-03-03T09:00:00")

    _w(root, "shop/orders.py", V1_ORDERS)
    c1 = _commit(root, "feat: order totals and coupons", "2025-03-04T10:00:00")

    _w(root, "shop/auth.py", V1_AUTH)
    c2 = _commit(root, "feat: password check", "2025-03-05T11:00:00")

    # 作者采纳部分评论后的 follow-up
    _w(root, "shop/orders.py", V2_ORDERS)
    c3 = _commit(
        root,
        "review: handle missing order, make discount a param",
        "2025-03-06T14:00:00",
    )
    _w(root, "shop/auth.py", V2_AUTH)
    c4 = _commit(
        root, "review: salted sha256 + parameterised query", "2025-03-06T15:30:00"
    )

    # 三周后的 bug-fix —— SZZ 要从这里回溯到 c1
    _w(root, "shop/orders.py", V3_ORDERS_FIX)
    c5 = _commit(
        root,
        "fix: apply_coupon raises KeyError when code does not match",
        "2025-03-27T16:00:00",
    )

    comments = _comments(c1, c2)
    (root / "comments.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in comments)
    )

    gt = {
        "commits": {
            "init": c0,
            "orders_v1": c1,
            "auth_v1": c2,
            "orders_review": c3,
            "auth_review": c4,
            "orders_bugfix": c5,
        },
        # SZZ 期望结果：c5 修的那一行，是 c1 引入的
        "szz_expected": {
            "fix_commit": c5,
            "inducing_commit": c1,
            "file": "shop/orders.py",
        },
        "n_comments": len(comments),
        "n_signal": sum(c["_gt_useful"] for c in comments),
    }
    (root / "groundtruth.json").write_text(json.dumps(gt, indent=2))
    return {"root": root, "comments": comments, "gt": gt}


def _c(cid, commit, path, line, ctype, author, body, useful, addressed):
    """一条 review 评论。`_gt_*` 前缀的字段是**我造数据时知道的真值**，
    真实数据里没有 —— pipeline 不许用它们，只能用来写断言。"""
    return {
        "comment_id": cid,
        "commit": commit,
        "path": path,
        "line": line,
        "type": ctype,
        "author": author,
        "body": body,
        "_gt_useful": useful,
        "_gt_addressed": addressed,
    }


def _comments(c1: str, c2: str) -> list:
    o, a = "shop/orders.py", "shop/auth.py"
    rows = [
        # ── orders.py 上的评论 ─────────────────────────────────────
        _c(
            "cm01",
            c1,
            o,
            18,
            "code_defect",
            "alice",
            "find_order returns None when the id is missing; every caller will "
            "hit an AttributeError. Raise KeyError or return a sentinel.",
            1,
            1,
        ),
        _c(
            "cm02",
            c1,
            o,
            3,
            "maintainability",
            "bob",
            "DISCOUNT as a module constant makes total() untestable. "
            "Pass it as a parameter with this as the default.",
            1,
            1,
        ),
        _c(
            "cm03",
            c1,
            o,
            23,
            "code_defect",
            "alice",
            "apply_coupon reads order['total'] even when the code does not match, "
            "so it KeyErrors for any other coupon.",
            1,
            0,
        ),  # ← 真信号但当时没被采纳
        _c("cm04", c1, o, 10, "nit_style", "carol", "nit: `s` -> `subtotal`", 0, 0),
        _c(
            "cm05",
            c1,
            o,
            1,
            "nit_style",
            "carol",
            "nit: stdlib imports should be in their own group",
            0,
            0,
        ),
        _c("cm06", c1, o, 12, "question", "dave", "Is qty ever a float here?", 0, 0),
        _c("cm07", c1, o, 9, "praise", "bob", "Nice, this is much cleaner 👍", 0, 0),
        _c(
            "cm08",
            c1,
            o,
            1,
            "bot",
            "codecov[bot]",
            "Coverage decreased (-0.4%) to 87.2%",
            0,
            0,
        ),
        _c(
            "cm09",
            c1,
            o,
            11,
            "performance",
            "dave",
            "This loop is O(n) — consider sum() with a generator.",
            0,
            0,
        ),  # 技术正确但无价值
        _c(
            "cm10",
            c1,
            o,
            5,
            "obsolete",
            "erin",
            "This references the old `read_orders` helper that was removed last week.",
            0,
            0,
        ),
        # ── auth.py 上的评论 ───────────────────────────────────────
        _c(
            "cm11",
            c2,
            a,
            4,
            "security",
            "alice",
            "MD5 for password hashing is broken. Use a salted KDF "
            "(sha256+salt at minimum, argon2/bcrypt preferably).",
            1,
            1,
        ),
        _c(
            "cm12",
            c2,
            a,
            7,
            "security",
            "alice",
            "String-concatenated SQL — this is injectable. Use a parameterised query.",
            1,
            1,
        ),
        _c(
            "cm13",
            c2,
            a,
            8,
            "code_defect",
            "bob",
            "`row and row[0] == ...` returns the row object when row is falsy; "
            "wrap in bool().",
            1,
            1,
        ),
        _c("cm14", c2, a, 3, "nit_style", "carol", "nit: two blank lines here", 0, 0),
        _c(
            "cm15",
            c2,
            a,
            1,
            "bot",
            "sonarqube[bot]",
            "1 Code Smell, 0 Bugs, 0 Vulnerabilities",
            0,
            0,
        ),
        _c("cm16", c2, a, 6, "question", "dave", "which db driver is this?", 0, 0),
        # ── 一条「看起来专业但是错的」—— 最难过滤的那类 ────────────────
        _c(
            "cm17",
            c2,
            a,
            4,
            "security",
            "frank",
            "hashlib is not thread-safe, wrap the call in a lock.",
            0,
            0,
        ),
    ]
    # 复制几条造出重复评论（真实 PR 里多人重复指出同一问题非常常见）
    rows.append(
        _c(
            "cm18",
            c2,
            a,
            4,
            "security",
            "grace",
            "Please don't use MD5 for passwords, it's not secure.",
            1,
            1,
        )
    )
    rows.append(
        _c(
            "cm19",
            c1,
            o,
            18,
            "code_defect",
            "heidi",
            "find_order can return None -> callers crash.",
            1,
            1,
        )
    )
    return rows


if __name__ == "__main__":
    out = build()
    gt = out["gt"]
    print(f"仓库 {out['root']}，{len(gt['commits'])} 个 commit")
    for k, v in gt["commits"].items():
        print(f"  {v[:7]}  {k}")
    print(
        f"\n评论 {gt['n_comments']} 条，其中真正有价值的 {gt['n_signal']} 条 "
        f"（{gt['n_signal'] / gt['n_comments']:.0%}）"
    )
    print("\n样例（前两条）：")
    for c in out["comments"][:2]:
        print(json.dumps(c, ensure_ascii=False, indent=2)[:340])
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/labs/cr_data/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/cr_data/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
