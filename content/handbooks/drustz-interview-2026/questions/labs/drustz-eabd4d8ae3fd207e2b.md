---
id: drustz-eabd4d8ae3fd207e2b
section: labs
order: 15
level: A
title: Exa 技术轮冷写题包（ML Research / ML Evals）
quick: 作者完整文档 · Exa 技术轮冷写题包（ML Research / ML Evals）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/exa_drills/README.md
    type: primary
---
# Exa 技术轮冷写题包（ML Research / ML Evals）

⏱ 本文件 4 分钟读完 ｜ 建于 2026-07-28，**2026-07-29 用第一轮实测结果修正**

## ⚠️ 第一轮实测：预测部分落空，先读这段

**2026-07-28 第一轮实际考的是「流式分位数」** —— 给一个 stream，返回任意 percentile。
推导路线：全排序 → 压缩空间 → 分桶 → 引入误差容忍 → **log 分桶算 index**。（答对了。）

| 我们原来的预测 | 实际 | 修正 |
|---|---|---|
| 检索指标 / 向量检索 / InfoNCE | **近似算法 + 空间/精度权衡** | Exa 的题偏**工程判断力**，不是 ML 配方背诵 |
| 「related to what we do at Exa」= ML 内容 | 是**搜索系统里的基础设施问题** | 索引压缩、剪枝、sketch、延迟预算都在射程内 |

→ 新增 **[Drill E · 流式分位数](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b)**（把那道题做完整：相对误差保证、可合并、滑动窗口）。
→ A–D 仍然值得练，但**优先级降到 Drill E 之后**。

**第二轮（2026-07-29 收到邀约）是 systems design**，不是 coding：
面试官 **Joshua Yurtsever**，方向是 production retrieval + post-training for agentic search
（reranking / snippet generation / model alignment）。
👉 **主备考文件换成 [20_case_exa_agentic_search.md](?book=drustz-interview-2026&section=mlsd&question=drustz-c5c2d47cc34774481f)**，本题包这轮只当热身。

## 官方 FAQ 要点（这决定了怎么练）

| 事实 | 对备考的含义 |
|---|---|
| 第一轮 45 min **live coding**，"related to what we do at Exa"，明确不是 LeetCode | 你的 [06](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) 是**口述 design** 弹药，对这轮不直接得分。要练手速 |
| 题面在 **Colab** 里，用**你自己的环境**共享屏幕 | 现在就要把 Colab 打通，别在面试里浪费时间 |
| ML 团队**必须用 Python** | 不用纠结语言 |
| **禁止任何 AI 工具**（virtual rounds；只有终轮 onsite 才 fully AI-enabled） | 这是你 pipeline 里风险最高的一轮。唯一的准备方式是冷写 |
| ~~第二轮 ML Research/Evals = **PyTorch 题**~~ | ❌ **已被推翻**：recruiter 原话是 "a more team specific question, that is often **systems design**" |
| 开场聊 recent projects + why Exa；结尾有 Q&A | 两头都要提前想好，见文末 |

## 五道题（概率已按第一轮实测重排）

| Drill | 主题 | timebox | 概率 | 对应轮次 |
|---|---|---|---|---|
| **[E · 流式分位数](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b)** | **DDSketch：log 桶、相对误差、可合并、滑动窗口** | 25 min | **★★★★★ 已考** | 第一轮实题 |
| [B · 向量检索](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b) | 批量 top-k、argpartition、**Matryoshka 截断级联** | 20 min | ★★★★☆ | 同类工程题 |
| [A · 检索评测指标](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b) | recall@k / MRR / **nDCG** / MAP，分级相关性 | 20 min | ★★★★☆ | design 轮口述也用得上 |
| [C · PyTorch InfoNCE](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b) | contrastive learning、温度、对称损失、假负例 mask | 25 min | ★★★☆☆ | work trial / onsite |
| [D · Judge 一致率](?book=drustz-interview-2026&section=labs&question=drustz-eabd4d8ae3fd207e2b) | kappa、position bias、Bradley-Terry、bootstrap CI | 20 min | ★★★☆☆ | Evals 岗对口 |

判断依据：E 是实考题；B/A/C/D 对应 Exa 官方博客反复讲的四件事——自训 embedding（C）、Matryoshka 截到 256 维省 20× 内存（B）、open evals 用 LLM 打 0–1 分级相关性（A、D）、GPT-4.1 judge 与人类 easy 97%/hard 83% 一致率（D）。

## 冷写协议（沿用你 `new/drills/` 那套）

```bash
cd exa_drills
cp drill_a_retrieval_metrics.py scratch.py
# 删掉 COLD-WRITE ZONE 里的所有实现体，保留签名和 docstring
# 计时，从记忆写，不看参考
/Users/mingrui/Documents/codes/interview/.venv/bin/python scratch.py
```



**卡住 10 分钟才允许看参考**；看懂后整段删掉重写。过关标准：连续两次一遍写对。

一键校验参考实现：
```bash
python3 run_all.py # 用 .venv 的 python，五个 drill 全跑
```



## 两三天的排法

| 时段 | 做什么 |
|---|---|
| **今天（最要紧）** | ① 打通 Colab（见下）② Drill A 冷写 ③ Drill C 冷写。这两道概率最高 |
| 明天 | Drill B + Drill D 冷写；A、C 各**重写一遍**（第二遍才算拥有） |
| 面试当天早上 | 四个 drill 的参考实现各读一遍 + 出声讲追问预演；**不要再写新题** |

## 环境清单（现在就做，别拖到面试当天）

- [ ] Colab 能登录、能新建 notebook、能跑 `import numpy, torch`
- [ ] 决定用 Colab 还是本地：你本地 `.venv` 是好的（torch 2.8 / numpy 2.0），但**题面在 Colab**，最省事的是直接在 Colab 里写
- [ ] 屏幕共享试一次（哪个显示器、字号调大到面试官能看清）
- [ ] **关掉所有 AI 补全**：Copilot、Cursor、Claude Code、IDE 里的 inline suggestion。面试前当着面关掉是加分项，被抓到是致命的
- [ ] 准备一个干净的 scratch notebook，预先 import 好 numpy/torch（省 30 秒）

## 45 分钟现场节奏

```text
0–3    听题 + 复述一遍确认理解 + 问清输入输出格式和规模
3–6    口述打算怎么做（先说最朴素的能跑版本），确认方向再动手
6–30   写。边写边讲。先让最小版本跑通，再优化
30–40  自测 + 优化 + 讲 trade-off（复杂度、内存、web 规模下怎么变）
40–45  Q&A
```



**最重要的一条**：先写能跑的朴素版本，再优化。FAQ 原话是 "we prioritize working code and seeing high level thinking in action"——**working code 排在第一位**。卡在追求最优解上不动手是最差的表现。

FAQ 还说 "you might not be familiar with the question or topic asked about; how do you think through it with the help of your interviewer?"——**这明确邀请你提问**。不懂就问，这是被鼓励的行为，不是扣分项。

## 开场：recent projects + why Exa

你最对口的一条线是 **eval / grader**，不是 agent：

> 我最近做的一块是把「主观质量」变成可自动计算的 grader，再用人工标注calibration它——包括论证旧的表面相似度指标其实是在掷硬币，以及构造扰动集去检验 grader 的判别力。这跟 Exa 在 evals 上的做法很像：你们用 LLM 给 (query, result) 打分级相关性，然后拿人类偏好去calibration judge，还专门做了 Exa Olympiad 那种困难 query 集。搜索质量的评测和我做的对话质量评测，难点是同一个：没有免费的 ground truth，只能用可验证信号加人工calibration去逼近。

**why Exa** 可以说：搜索是少数几个「评测本身就是核心研究问题」的方向——他们放弃 MS Marco 式封闭评测、自己搭 open evals，说明这家公司认真对待这件事。

## 结尾 Q&A 问什么（他们说会留时间）

挑两三个，别问官网能查到的：
- open evals 里 Exa Olympiad 那批困难 query 是怎么构造和维护的？会随模型变强而更新吗？
- pointwise 打分在跨版本追踪上会不会漂移（judge 模型升级导致历史分数不可比）？怎么处理？
- Matryoshka 的维度是怎么定的？粗筛维度和 shortlist 大小是一起调的吗？
- 从网页挖 embedding 训练数据——最大的噪声来源是什么？
- ML Research 和 ML Evals 两个团队日常怎么协作？

## 相关材料

- 设计题弹药（第二轮若是 design，或 onsite）：[06_search_post_training.md](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2)
- Exa 公司卡（一手事实与接话点）：[13_company_cards.md](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9)
- 概念版实验（纯 Python，讲原理用）：[lab03_retrieval_negatives](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab03_retrieval_negatives/)
- 通用 PyTorch 冷写：[`../../../online_resource/drills/`](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/drills/)

## drill_a_retrieval_metrics.py

```python
"""Drill A · 检索评测指标(recall@k / precision@k / MRR / nDCG / MAP)

⏱ timebox 20 分钟  ｜  概率评级:★★★★★(ML Evals 岗第一顺位)

为什么是这道题:Exa 的 evals-at-exa 讲的就是「怎么给搜索结果打分」。
他们用 LLM 对 (query, result) 打 0–1 的**分级**相关性,分级相关性最自然的
指标就是 nDCG。这题几乎是他们日常工作的最小复现。

冷写协议:
    cp drill_a_retrieval_metrics.py scratch.py
    删掉 COLD-WRITE ZONE 里的实现体(保留签名和 docstring)
    计时 20 分钟从记忆写 -> python3 scratch.py -> 红了就修,不看参考

面试时必须能顺口说出来的:
    * nDCG 的折扣是 log2(i+1),i 从 1 开始 -> 第 1 位折扣为 1
    * IDCG 是「把相关性降序排好」的 DCG;IDCG=0 时 nDCG 定义为 0
    * MRR 只看第一个相关结果 -> 适合「有唯一正确答案」的场景
    * recall@k 的分母是**全部**相关文档数,不是 k
    * 二值相关性用 MAP/MRR,分级相关性用 nDCG
"""

import math
from typing import Dict, List, Sequence

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def recall_at_k(ranked: Sequence[str], relevant: Sequence[str], k: int) -> float:
    """top-k 里命中了多少比例的**全部**相关文档。

    分母是 len(relevant),不是 k —— 这是最常见的口误。
    relevant 为空时返回 0.0(而不是崩掉)。
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    hit = sum(1 for d in ranked[:k] if d in rel)
    return hit / len(rel)


def precision_at_k(ranked: Sequence[str], relevant: Sequence[str], k: int) -> float:
    """top-k 里有多少比例是相关的。分母是 k(不足 k 时按实际长度)。"""
    if k <= 0:
        return 0.0
    window = ranked[:k]
    if not window:
        return 0.0
    rel = set(relevant)
    return sum(1 for d in window if d in rel) / len(window)


def reciprocal_rank(
    ranked: Sequence[str], relevant: Sequence[str], k: int = None
) -> float:
    """第一个相关结果排名的倒数;top-k 内没有相关结果则 0。"""
    rel = set(relevant)
    window = ranked if k is None else ranked[:k]
    for i, d in enumerate(window, start=1):
        if d in rel:
            return 1.0 / i
    return 0.0


def dcg_at_k(gains: Sequence[float], k: int) -> float:
    """DCG = Σ_{i=1..k} gain_i / log2(i + 1)。

    注意 i 从 1 开始,所以第 1 位的折扣是 log2(2)=1(不打折)。
    """
    return sum(g / math.log2(i + 1) for i, g in enumerate(gains[:k], start=1))


def ndcg_at_k(ranked: Sequence[str], gain_by_doc: Dict[str, float], k: int) -> float:
    """分级相关性下的归一化 DCG。

    IDCG = 把所有已知的相关性分数降序排列后取前 k 的 DCG。
    IDCG == 0(没有任何相关文档)时返回 0.0。
    """
    gains = [gain_by_doc.get(d, 0.0) for d in ranked[:k]]
    ideal = sorted(gain_by_doc.values(), reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0.0:
        return 0.0
    return dcg_at_k(gains, k) / idcg


def average_precision_at_k(
    ranked: Sequence[str], relevant: Sequence[str], k: int
) -> float:
    """AP@k:每命中一个相关文档就记一次 precision@该位置,再对相关文档总数取平均。

    分母用 min(len(relevant), k) —— 否则 k 小于相关文档数时 AP 永远拿不到 1。
    """
    rel = set(relevant)
    if not rel:
        return 0.0
    hits = 0
    acc = 0.0
    for i, d in enumerate(ranked[:k], start=1):
        if d in rel:
            hits += 1
            acc += hits / i
    denom = min(len(rel), k)
    return acc / denom if denom else 0.0


def evaluate(runs: List[dict], k: int = 10) -> Dict[str, float]:
    """对一批 query 求各指标均值。

    runs 里每项: {"ranked": [doc_id...], "gains": {doc_id: 相关性分数}}
    二值场景把 gains 的值设成 0/1 即可。
    """
    if not runs:
        return {}
    out = {
        "recall@k": 0.0,
        "precision@k": 0.0,
        "mrr@k": 0.0,
        "ndcg@k": 0.0,
        "map@k": 0.0,
    }
    for r in runs:
        ranked, gains = r["ranked"], r["gains"]
        relevant = [d for d, g in gains.items() if g > 0]
        out["recall@k"] += recall_at_k(ranked, relevant, k)
        out["precision@k"] += precision_at_k(ranked, relevant, k)
        out["mrr@k"] += reciprocal_rank(ranked, relevant, k)
        out["ndcg@k"] += ndcg_at_k(ranked, gains, k)
        out["map@k"] += average_precision_at_k(ranked, relevant, k)
    return {m: v / len(runs) for m, v in out.items()}


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    # --- nDCG 手算校验 ---
    gains = {"a": 3.0, "b": 2.0, "c": 3.0, "d": 0.0, "e": 1.0, "f": 2.0}
    ranked = ["a", "b", "c", "d", "e", "f"]
    # DCG@6 = 3/1 + 2/log2(3) + 3/2 + 0/log2(5) + 1/log2(6) + 2/log2(7)
    expect_dcg = (
        3 / 1
        + 2 / math.log2(3)
        + 3 / math.log2(4)
        + 0 / math.log2(5)
        + 1 / math.log2(6)
        + 2 / math.log2(7)
    )
    got = dcg_at_k([gains[d] for d in ranked], 6)
    assert abs(got - expect_dcg) < 1e-9, (got, expect_dcg)

    # 完美排序的 nDCG 必须是 1
    perfect = sorted(gains, key=lambda d: -gains[d])
    assert abs(ndcg_at_k(perfect, gains, 6) - 1.0) < 1e-12
    # 打乱后必须 <= 1
    assert ndcg_at_k(["d", "e", "f", "a", "b", "c"], gains, 6) < 1.0
    # 全不相关 -> 0
    assert ndcg_at_k(["x", "y"], {"x": 0.0, "y": 0.0}, 2) == 0.0

    # --- recall/precision ---
    r = ["d1", "d2", "d3", "d4"]
    rel = ["d2", "d4", "d9"]  # d9 不在结果里
    assert abs(recall_at_k(r, rel, 4) - 2 / 3) < 1e-12  # 分母是 3 不是 4
    assert abs(precision_at_k(r, rel, 4) - 2 / 4) < 1e-12
    assert abs(precision_at_k(r, rel, 2) - 1 / 2) < 1e-12
    assert recall_at_k(r, [], 4) == 0.0

    # --- MRR ---
    assert reciprocal_rank(["a", "b", "c"], ["b"]) == 0.5
    assert reciprocal_rank(["a", "b", "c"], ["c"], k=2) == 0.0  # 截断后没命中
    assert reciprocal_rank(["a"], ["z"]) == 0.0

    # --- AP ---
    # 命中在第 1、3 位: (1/1 + 2/3)/2
    ap = average_precision_at_k(["a", "x", "b", "y"], ["a", "b"], 4)
    assert abs(ap - (1.0 + 2 / 3) / 2) < 1e-12
    # 相关文档数 > k 时分母用 k
    ap2 = average_precision_at_k(["a", "b"], ["a", "b", "c", "d"], 2)
    assert abs(ap2 - 1.0) < 1e-12

    # --- 汇总 ---
    runs = [{"ranked": ranked, "gains": gains}, {"ranked": perfect, "gains": gains}]
    agg = evaluate(runs, k=6)
    assert 0.0 < agg["ndcg@k"] <= 1.0
    assert abs(agg["recall@k"] - 1.0) < 1e-12  # 两次都召回了全部相关文档

    print("  全部断言通过")
    print("  示例汇总(k=6):")
    for m, v in agg.items():
        print("    {:<14}{:.4f}".format(m, v))


if __name__ == "__main__":
    print("Drill A · 检索评测指标")
    _tests()
    print("""
面试追问预演:
  Q 为什么用 nDCG 不用 precision?
  A 搜索结果的相关性是**分级**的而不是二值的,而且位置很重要 ——
    nDCG 同时处理了这两点。Exa 用 LLM 给 (query,result) 打 0–1 分,
    正好是分级相关性。

  Q nDCG 的局限?
  A ① IDCG 依赖「已知的相关文档集合」,而 web 规模下这个集合永远不完整
       -> 未标注的相关文档被当成 gain=0,系统性低估好系统(这正是 Exa
       放弃 MS Marco 式封闭评测的理由之一);
     ② 跨 query 平均会被「容易的 query」主导,要分层报告;
     ③ 折扣函数是约定俗成的,不等于真实用户的注意力衰减。

  Q recall@k 在 web 搜索里怎么算?
  A 严格意义算不了 —— 分母(全部相关文档)未知。实践中用 pooling:
    把多个系统的 top-k 并起来人工/LLM 判定,当作近似的相关集合。
""")
```




## drill_b_vector_search.py

```python
"""Drill B · 向量检索:批量 top-k、Matryoshka 截断、两段级联

⏱ timebox 20 分钟  ｜  概率评级:★★★★☆

为什么是这道题:Exa 自己训 embedding、自建 web-scale 向量库,并且明确用了
Matryoshka(2048 维截到 256 维,内存降 20x)。「写一个向量检索」是最直接的
「related to what we do at Exa」。

冷写协议:
    cp drill_b_vector_search.py scratch.py  -> 删实现体 -> 计时 20 分钟

面试时必须能顺口说出来的:
    * 归一化之后,cosine 相似度就是点积 -> 一次矩阵乘搞定全部 query x doc
    * 取 top-k 用 argpartition 是 O(n),argsort 是 O(n log n);
      只在选出的 k 个里再排序
    * Matryoshka: 前 m 维本身就是一个可用 embedding -> 用它做全库粗筛,
      再用全维精排 top-k。省的是**全库**扫描成本
    * 精排只作用于 shortlist,所以「加大 shortlist」是便宜的召回补救
"""

import numpy as np

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def l2_normalize(x: np.ndarray, axis: int = -1, eps: float = 1e-12) -> np.ndarray:
    """按行归一化。eps 防止零向量除零。"""
    norm = np.linalg.norm(x, axis=axis, keepdims=True)
    return x / np.maximum(norm, eps)


def cosine_scores(queries: np.ndarray, docs: np.ndarray) -> np.ndarray:
    """(Q, D) 相似度矩阵。归一化后 cosine == 点积。

    queries: (Q, dim)   docs: (D, dim)   ->  (Q, D)
    """
    return l2_normalize(queries) @ l2_normalize(docs).T


def top_k(scores: np.ndarray, k: int):
    """按行取 top-k。返回 (indices, values),都按分数降序。

    用 argpartition 先 O(n) 选出 k 个候选,再只对这 k 个排序。
    k >= D 时退化为全排序。
    """
    q, d = scores.shape
    k = min(k, d)
    # argpartition 保证第 -k 位左边都不大于右边;取最后 k 列即 top-k(无序)
    idx = np.argpartition(-scores, kth=k - 1, axis=1)[:, :k]
    vals = np.take_along_axis(scores, idx, axis=1)
    order = np.argsort(-vals, axis=1)  # 只对 k 个排序
    idx = np.take_along_axis(idx, order, axis=1)
    vals = np.take_along_axis(vals, order, axis=1)
    return idx, vals


def search(queries: np.ndarray, docs: np.ndarray, k: int = 10):
    """朴素全量检索:全维打分 + top-k。"""
    return top_k(cosine_scores(queries, docs), k)


def matryoshka_search(
    queries: np.ndarray,
    docs: np.ndarray,
    coarse_dim: int,
    shortlist_k: int,
    final_k: int = 10,
):
    """两段级联:前 coarse_dim 维全库粗筛 -> shortlist 上用全维精排。

    关键实现细节:截断之后**必须重新归一化**,因为前 m 维的范数不是 1。
    返回 (indices, values, cost),cost 按乘加次数计。
    """
    n_docs, dim = docs.shape
    coarse_dim = min(coarse_dim, dim)
    shortlist_k = min(shortlist_k, n_docs)

    # --- 粗筛:只用前 coarse_dim 维 ---
    cand_idx, _ = top_k(
        cosine_scores(queries[:, :coarse_dim], docs[:, :coarse_dim]), shortlist_k
    )

    # --- 精排:每个 query 只在自己的 shortlist 上用全维打分 ---
    qn = l2_normalize(queries)
    dn = l2_normalize(docs)
    final_k = min(final_k, shortlist_k)
    out_idx = np.empty((len(queries), final_k), dtype=np.int64)
    out_val = np.empty((len(queries), final_k), dtype=float)
    for qi in range(len(queries)):
        cands = cand_idx[qi]
        s = dn[cands] @ qn[qi]
        order = np.argsort(-s)[:final_k]
        out_idx[qi] = cands[order]
        out_val[qi] = s[order]

    cost = len(queries) * (n_docs * coarse_dim + shortlist_k * dim)
    return out_idx, out_val, cost


def recall_vs_exact(approx_idx: np.ndarray, exact_idx: np.ndarray) -> float:
    """近似检索相对精确检索的 recall(逐 query 求交集比例再平均)。"""
    per_q = [
        len(set(a.tolist()) & set(e.tolist())) / len(e)
        for a, e in zip(approx_idx, exact_idx)
    ]
    return float(np.mean(per_q))


def apply_matryoshka_profile(x: np.ndarray, decay: float = 0.035) -> np.ndarray:
    """把「各维等权」的向量改造成「前缀信息量更大」的向量。

    这是在**模拟** Matryoshka 训练的效果:训练时对每个前缀长度都算一次
    损失,模型于是学会把最重要的信息压进前面的维度。
    这里用一条指数衰减的每维权重来近似同样的结构。

    面试要点:前缀可截断**不是向量的天然性质**,是训练目标带来的。
    对一个普通 embedding 直接砍维度,召回会掉得很惨(见 _tests 的对照)。
    """
    dim = x.shape[-1]
    weights = np.exp(-decay * np.arange(dim))
    return x * weights


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    rng = np.random.default_rng(0)
    D, DIM, Q = 4000, 128, 16
    docs = rng.normal(size=(D, DIM))
    # 让 query 有真实近邻:从若干文档加噪声派生
    anchors = rng.choice(D, size=Q, replace=False)
    queries = docs[anchors] + 0.35 * rng.normal(size=(Q, DIM))

    # --- 归一化 ---
    n = l2_normalize(docs)
    assert np.allclose(np.linalg.norm(n, axis=1), 1.0)
    assert np.allclose(l2_normalize(np.zeros((2, 4))), 0.0)  # 零向量不炸

    # --- cosine 与手算一致 ---
    s = cosine_scores(queries[:3], docs[:5])
    for i in range(3):
        for j in range(5):
            man = (
                queries[i]
                @ docs[j]
                / (np.linalg.norm(queries[i]) * np.linalg.norm(docs[j]))
            )
            assert abs(s[i, j] - man) < 1e-10
    assert (s <= 1.0 + 1e-9).all() and (s >= -1.0 - 1e-9).all()

    # --- top_k 与全排序一致 ---
    full = cosine_scores(queries, docs)
    idx, vals = top_k(full, 10)
    ref = np.argsort(-full, axis=1)[:, :10]
    assert (idx == ref).all(), "top_k 应与 argsort 结果一致"
    assert (np.diff(vals, axis=1) <= 1e-12).all(), "必须降序"
    # 每个 query 命中自己的 anchor
    assert all(anchors[i] in idx[i] for i in range(Q))

    # k 超过文档数不应崩
    small_idx, _ = top_k(full[:, :5], 50)
    assert small_idx.shape == (Q, 5)

    # --- 级联:普通 embedding vs Matryoshka 式 embedding 对照 ---
    m_docs = apply_matryoshka_profile(docs)
    m_queries = apply_matryoshka_profile(queries)

    exact_idx, _ = search(queries, docs, k=10)
    m_exact_idx, _ = search(m_queries, m_docs, k=10)
    full_cost = Q * D * DIM

    print("  截断粗筛的召回:普通 embedding vs Matryoshka 式(shortlist=100)")
    print(
        "  {:<12}{:<16}{:<18}{}".format(
            "coarse_dim", "普通 recall", "Matryoshka recall", "成本"
        )
    )
    for cdim in (128, 64, 32, 16, 8):
        sk = 10 if cdim == DIM else 100
        a_idx, _, cost = matryoshka_search(queries, docs, cdim, sk, final_k=10)
        rec = recall_vs_exact(a_idx, exact_idx)
        m_idx, _, _ = matryoshka_search(m_queries, m_docs, cdim, sk, final_k=10)
        m_rec = recall_vs_exact(m_idx, m_exact_idx)
        print(
            "  {:<12}{:<16.3f}{:<18.3f}{:>9}  ({:>3.0f}% of full)".format(
                cdim, rec, m_rec, cost, 100 * cost / full_cost
            )
        )
        if cdim == DIM:
            assert rec == 1.0 and m_rec == 1.0, "全维粗筛必须无损"

    # 同样截到 1/4 维,Matryoshka 式明显更抗截断
    r32 = recall_vs_exact(matryoshka_search(queries, docs, 32, 100)[0], exact_idx)
    m32 = recall_vs_exact(matryoshka_search(m_queries, m_docs, 32, 100)[0], m_exact_idx)
    assert m32 > r32, "Matryoshka 式应当更抗截断: {:.3f} vs {:.3f}".format(m32, r32)

    # 截断越狠召回越差(单调性,允许同分)
    r64 = recall_vs_exact(matryoshka_search(queries, docs, 64, 100)[0], exact_idx)
    r8 = recall_vs_exact(matryoshka_search(queries, docs, 8, 100)[0], exact_idx)
    assert r64 >= r8, "更多维度不应更差"

    # 加大 shortlist 能买回召回
    r_small = recall_vs_exact(matryoshka_search(queries, docs, 16, 30)[0], exact_idx)
    r_big = recall_vs_exact(matryoshka_search(queries, docs, 16, 400)[0], exact_idx)
    assert r_big >= r_small
    print(
        "\n  普通 embedding, coarse_dim=16: shortlist 30 -> 400 召回 {:.3f} -> {:.3f}".format(
            r_small, r_big
        )
    )
    print("  -> 两条补救路径:把 embedding 训成可截断的(Matryoshka),")
    print("     或者留着普通 embedding 但加大 shortlist。前者省内存,后者省训练。")
    print("  全部断言通过")


if __name__ == "__main__":
    print("Drill B · 向量检索与 Matryoshka 级联")
    _tests()
    print("""
面试追问预演:
  Q 为什么不用 argsort?
  A argpartition 是 O(n) 选出 top-k,argsort 是 O(n log n) 排全部。
    D 上百万时差距很大,而我们只关心前 k 个的顺序。

  Q 这个还不是 ANN,真实系统怎么做?
  A 这里是精确暴力检索,复杂度 O(N·dim)。web 规模要上 ANN:
    HNSW(图索引,高召回低延迟,内存大)或 IVF-PQ(倒排+量化,十亿级、
    内存受限时用)。Matryoshka 截断可以和两者叠加 —— 它降的是每次
    距离计算的维度,ANN 降的是要算多少次。

  Q 截断为什么要重新归一化?
  A 前 m 维的子向量范数不是 1,不重新归一化就不是 cosine 了,
    会偏向那些「能量集中在前 m 维」的文档。

  Q 怎么选 coarse_dim?
  A 不是猜,是画 recall-成本曲线:固定 shortlist 扫 coarse_dim,
    找召回开始掉的拐点。掉了还可以用更大的 shortlist 买回来,
    因为精排只作用于 k 条。
""")
```




## drill_c_infonce_pytorch.py

```python
"""Drill C · PyTorch 手写 InfoNCE / 对比学习(第二轮 PyTorch 题主力)

⏱ timebox 25 分钟  ｜  概率评级:★★★★★(ML Research/Evals 第二轮)

为什么是这道题:Exa 自己预训练+微调 embedding 模型。「手写 contrastive loss」
是 embedding 训练最核心的一块,也是最容易在细节上翻车的一块。

冷写协议:
    cp drill_c_infonce_pytorch.py scratch.py -> 删实现体 -> 计时 25 分钟

五个必须记住的坑(面试官八成会挑其中一个问):
    1. **忘记归一化** -> 点积不是 cosine,温度的含义全变,训练不稳
    2. **温度是除不是乘**: logits = sim / T。T 越小分布越尖、对 hard negative
       越敏感;T 太小会梯度饱和
    3. **labels 是 arange(B)** —— 第 i 个 query 的正例是第 i 个 doc(对角线)
    4. **对称损失**: query->doc 和 doc->query 两个方向都要算(CLIP 的做法),
       只算一个方向会让两侧编码器学得不对称
    5. **batch 内重复正例 = 假负例**:同一篇文档出现两次,或两个 query 指向
       同一文档时,它会被当成别人的负例 -> 必须 mask 掉
"""

import torch
import torch.nn.functional as F

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def info_nce_in_batch(
    q: torch.Tensor, d: torch.Tensor, temperature: float = 0.05, symmetric: bool = True
) -> torch.Tensor:
    """标准 in-batch negatives 版 InfoNCE。

    q: (B, dim) query 向量   d: (B, dim) 正例文档向量,d[i] 是 q[i] 的正例
    其余 B-1 个文档充当负例。

    返回标量 loss。
    """
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    logits = q @ d.t() / temperature  # (B, B),对角线是正例
    labels = torch.arange(q.size(0), device=q.device)
    loss = F.cross_entropy(logits, labels)
    if symmetric:
        # 反方向:每个 doc 找回自己的 query
        loss = 0.5 * (loss + F.cross_entropy(logits.t(), labels))
    return loss


def info_nce_with_hard_negatives(
    q: torch.Tensor, pos: torch.Tensor, negs: torch.Tensor, temperature: float = 0.05
) -> torch.Tensor:
    """显式负例版:每个 query 自带一组挖来的 hard negatives。

    q:    (B, dim)
    pos:  (B, dim)
    negs: (B, N, dim)

    做法:把正例拼到负例前面 -> (B, 1+N),标签恒为 0。
    """
    q = F.normalize(q, dim=-1)
    pos = F.normalize(pos, dim=-1)
    negs = F.normalize(negs, dim=-1)

    pos_logit = (q * pos).sum(-1, keepdim=True)  # (B, 1)
    neg_logits = torch.bmm(negs, q.unsqueeze(-1)).squeeze(-1)  # (B, N)
    logits = torch.cat([pos_logit, neg_logits], dim=1) / temperature
    labels = torch.zeros(q.size(0), dtype=torch.long, device=q.device)
    return F.cross_entropy(logits, labels)


def build_false_negative_mask(doc_ids: torch.Tensor) -> torch.Tensor:
    """batch 内同一篇文档出现多次时,把「非自己位置的同一文档」标记出来。

    doc_ids: (B,) 每个位置对应的文档 id
    返回 (B, B) 的 bool mask,True = 需要屏蔽的假负例(不含对角线)。
    """
    same = doc_ids.unsqueeze(0) == doc_ids.unsqueeze(1)  # (B, B)
    eye = torch.eye(len(doc_ids), dtype=torch.bool, device=doc_ids.device)
    return same & ~eye


def info_nce_masked(
    q: torch.Tensor, d: torch.Tensor, doc_ids: torch.Tensor, temperature: float = 0.05
) -> torch.Tensor:
    """带假负例屏蔽的 InfoNCE。

    屏蔽方式是把对应 logit 设成 -inf,让它在 softmax 里权重为 0。
    注意:要在**除以温度之后**再填 -inf,顺序不影响结果但别写成 -1e9 加在
    归一化前(数值上不干净)。
    """
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    logits = q @ d.t() / temperature
    mask = build_false_negative_mask(doc_ids)
    logits = logits.masked_fill(mask, float("-inf"))
    labels = torch.arange(q.size(0), device=q.device)
    return F.cross_entropy(logits, labels)


def retrieval_accuracy(q: torch.Tensor, d: torch.Tensor) -> float:
    """batch 内 top-1 检索准确率,训练时最直观的健康指标。"""
    q = F.normalize(q, dim=-1)
    d = F.normalize(d, dim=-1)
    pred = (q @ d.t()).argmax(dim=1)
    labels = torch.arange(q.size(0), device=q.device)
    return (pred == labels).float().mean().item()


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    torch.manual_seed(0)
    B, DIM = 8, 16

    # --- 完美对齐时 loss 应当接近 0 ---
    d = F.normalize(torch.randn(B, DIM), dim=-1)
    loss_perfect = info_nce_in_batch(d.clone(), d.clone(), temperature=0.05)
    assert loss_perfect.item() < 1e-3, loss_perfect.item()

    # --- 随机时 loss 应当接近 ln(B) ---
    q_rand, d_rand = torch.randn(B, DIM), torch.randn(B, DIM)
    loss_rand = info_nce_in_batch(q_rand, d_rand, temperature=1.0)
    import math

    assert abs(loss_rand.item() - math.log(B)) < 0.6, loss_rand.item()

    # --- 与手算 cross entropy 一致(非对称版) ---
    qn, dn = F.normalize(q_rand, dim=-1), F.normalize(d_rand, dim=-1)
    logits = qn @ dn.t() / 0.05
    manual = -torch.log_softmax(logits, dim=1).diag().mean()
    got = info_nce_in_batch(q_rand, d_rand, 0.05, symmetric=False)
    assert torch.allclose(manual, got, atol=1e-6)

    # --- 对称版 = 两个方向的平均 ---
    rev = -torch.log_softmax(logits.t(), dim=1).diag().mean()
    sym = info_nce_in_batch(q_rand, d_rand, 0.05, symmetric=True)
    assert torch.allclose(0.5 * (manual + rev), sym, atol=1e-6)

    # --- 忘记归一化会改变结果(证明这一步不是可选的) ---
    raw_logits = q_rand @ d_rand.t() / 0.05
    raw_loss = F.cross_entropy(raw_logits, torch.arange(B))
    assert not torch.allclose(raw_loss, got, atol=1e-3), "归一化必须影响结果"

    # --- 温度效应:更小的温度让同样的排序产生更极端的 loss ---
    l_hot = info_nce_in_batch(q_rand, d_rand, 0.02, symmetric=False)
    l_cold = info_nce_in_batch(q_rand, d_rand, 1.0, symmetric=False)
    assert l_hot.item() > l_cold.item(), "随机初始化下,低温会放大惩罚"

    # --- hard negative 版 ---
    q = F.normalize(torch.randn(B, DIM), dim=-1)
    pos = F.normalize(q + 0.1 * torch.randn(B, DIM), dim=-1)  # 与 q 很像
    easy = F.normalize(torch.randn(B, 4, DIM), dim=-1)
    hard = F.normalize(q.unsqueeze(1) + 0.5 * torch.randn(B, 4, DIM), dim=-1)
    l_easy = info_nce_with_hard_negatives(q, pos, easy)
    l_hard = info_nce_with_hard_negatives(q, pos, hard)
    assert l_hard.item() > l_easy.item(), "hard negative 的 loss 必须更大"

    # --- 假负例屏蔽 ---
    doc_ids = torch.tensor([0, 1, 2, 2, 4, 5, 6, 7])  # 位置 2、3 是同一篇文档
    mask = build_false_negative_mask(doc_ids)
    assert mask[2, 3] and mask[3, 2]
    assert not mask[2, 2] and not mask[0, 1]
    assert mask.sum().item() == 2

    l_plain = info_nce_in_batch(q_rand, d_rand, 0.05, symmetric=False)
    l_masked = info_nce_masked(q_rand, d_rand, doc_ids, 0.05)
    assert l_masked.item() <= l_plain.item() + 1e-6, "屏蔽掉一个负例后 loss 不应变大"
    assert torch.isfinite(l_masked), "-inf 屏蔽后仍须是有限值"

    # --- 梯度确实回传 ---
    p = torch.randn(B, DIM, requires_grad=True)
    info_nce_in_batch(p, d_rand).backward()
    assert p.grad is not None and torch.isfinite(p.grad).all()
    assert p.grad.abs().sum() > 0

    # --- 真训一小步,loss 必须下降、batch 内 top-1 必须上升 ---
    torch.manual_seed(1)
    docs = F.normalize(torch.randn(B, DIM), dim=-1)
    qv = torch.randn(B, DIM, requires_grad=True)
    opt = torch.optim.Adam([qv], lr=0.1)
    first = info_nce_in_batch(qv, docs).item()
    acc0 = retrieval_accuracy(qv.detach(), docs)
    for _ in range(120):
        opt.zero_grad()
        loss = info_nce_in_batch(qv, docs)
        loss.backward()
        opt.step()
    last = info_nce_in_batch(qv, docs).item()
    acc1 = retrieval_accuracy(qv.detach(), docs)
    assert last < first, (first, last)
    assert acc1 >= acc0

    print("  全部断言通过")
    print(
        "  完美对齐 loss = {:.6f}   随机 loss ≈ ln(B) = {:.4f}".format(
            loss_perfect.item(), math.log(B)
        )
    )
    print(
        "  easy negatives loss = {:.4f}   hard negatives loss = {:.4f}".format(
            l_easy.item(), l_hard.item()
        )
    )
    print(
        "  训练 120 步: loss {:.4f} -> {:.4f}   batch top-1 {:.2f} -> {:.2f}".format(
            first, last, acc0, acc1
        )
    )


if __name__ == "__main__":
    print("Drill C · PyTorch InfoNCE")
    _tests()
    print("""
面试追问预演:
  Q batch size 为什么对 contrastive 这么重要?
  A in-batch negatives 的数量就是 B-1。B 越大,softmax 的分母里负例越多,
    梯度信号越强、估计的对比分布越接近全库。所以业界会用很大的 batch
    (几万级),工程上靠 gradient cache / 跨卡收集 in-batch negatives 实现。

  Q 温度怎么选?
  A 太小 -> softmax 饱和,梯度消失,而且对标注噪声极敏感;太大 -> 区分不出
    hard 和 easy。常见 0.01–0.1,要在 dev set 上扫。有些实现把它做成可学习
    参数(CLIP 就是,用 log 参数化并做上限裁剪)。

  Q 为什么要对称 loss?
  A 只算 query->doc 时,doc 侧编码器只通过负例得到梯度,两侧会学得不对称。
    CLIP 式对称损失让两个方向都有正例梯度。

  Q in-batch negatives 有什么隐患?
  A 假负例。batch 里可能混进对当前 query 也相关的文档,却被当成负例。
    两种处理:① 按文档 id 去重并 mask(本 drill 的 build_false_negative_mask);
    ② 更狠的做法是用 cross-encoder 给候选打分,过滤掉与正例太像的。
    这也是 Exa 放弃 MS Marco 式稀疏标注评测的同一个病根。

  Q 显存不够放大 batch 怎么办?
  A GradCache:先不建图跑一遍拿到所有 embedding 和对比矩阵的梯度,
    再分块重跑带图的前向把梯度接上。用两遍前向换 O(B) 显存。
""")
```




## drill_d_judge_agreement.py

```python
"""Drill D · LLM judge 的一致率、位置偏差与系统对比(evals-at-exa 对口)

⏱ timebox 20 分钟  ｜  概率评级:★★★★☆(ML Evals 岗高度对口)

为什么是这道题:Exa 的 evals-at-exa 博客写得很具体 —— 用 GPT-4.1 做 judge、
五个维度打 0–1 分、与人类偏好一致率 easy 97% / hard 83%、pointwise 与
pairwise(ELO)、listwise 都试过而默认 pointwise。这道题就是那套东西的代码版。

冷写协议:
    cp drill_d_judge_agreement.py scratch.py -> 删实现体 -> 计时 20 分钟

四个必须能说的点:
    1. **raw agreement 会骗人**:类别不平衡时瞎猜也能很高 -> 要报 Cohen's kappa
    2. **位置偏差必须测**:同一对结果交换顺序再问一次,统计翻转率
    3. **难易分层报告**:整体 90% 可能是「简单样本 97% + 困难样本 60%」
    4. **系统对比要给置信区间**:按 query bootstrap,不是按 (query,result) 对
"""

from typing import Dict, List, Sequence, Tuple

import numpy as np

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def raw_agreement(a: Sequence, b: Sequence) -> float:
    """两个标注者逐项完全一致的比例。"""
    assert len(a) == len(b) and len(a) > 0
    return float(np.mean([x == y for x, y in zip(a, b)]))


def cohens_kappa(a: Sequence, b: Sequence) -> float:
    """Cohen's kappa:扣掉「碰巧一致」之后的一致率。

    kappa = (p_o - p_e) / (1 - p_e)
      p_o = 实际一致率
      p_e = 两人各自的边缘分布下随机一致的期望 = Σ_c p_a(c)·p_b(c)

    解读:<0 比瞎猜还差;0.2-0.4 一般;0.4-0.6 中等;0.6-0.8 较好;>0.8 很好。
    p_e == 1(两人都只用同一个标签)时定义为 0.0。
    """
    assert len(a) == len(b) and len(a) > 0
    labels = sorted(set(a) | set(b))
    n = len(a)
    p_o = raw_agreement(a, b)
    p_e = 0.0
    for c in labels:
        p_e += (sum(1 for x in a if x == c) / n) * (sum(1 for y in b if y == c) / n)
    if abs(1.0 - p_e) < 1e-12:
        return 0.0
    return (p_o - p_e) / (1.0 - p_e)


def position_bias_rate(forward: Sequence[str], swapped: Sequence[str]) -> float:
    """同一对候选,交换呈现顺序再判一次,统计**不自洽**的比例。

    约定:两次都用 "A"/"B" 表示「呈现在第一位/第二位的那个」。
    自洽 = 交换后判断也跟着翻转。例如正着判 A 赢,反着就该判 B 赢。
    返回 0 表示无位置偏差,0.5 表示判断与内容无关。
    """
    assert len(forward) == len(swapped) and len(forward) > 0
    flip = {"A": "B", "B": "A"}
    inconsistent = sum(
        1
        for f, s in zip(forward, swapped)
        if s != flip.get(f, s)  # 平局等其他标签视为一致,不计入
    )
    return inconsistent / len(forward)


def debias_pairwise(forward: Sequence[str], swapped: Sequence[str]) -> List[str]:
    """双向判定的去偏聚合:两次一致才算数,不一致记 "tie"。

    这是最便宜也最常用的位置去偏做法 —— 代价是 judge 调用翻倍。
    返回每项的胜者,用**内容标识**表示:"first" 指正向呈现时排第一的那个。
    """
    flip = {"A": "B", "B": "A"}
    out = []
    for f, s in zip(forward, swapped):
        if f in flip and s == flip[f]:
            out.append("first" if f == "A" else "second")
        else:
            out.append("tie")
    return out


def bradley_terry(
    pairs: Sequence[Tuple[str, str]], iters: int = 500
) -> Dict[str, float]:
    """从成对胜负拟合 Bradley-Terry 强度(MM 迭代)。

    pairs: [(winner, loser), ...]
    模型: P(i 胜 j) = p_i / (p_i + p_j)
    迭代: p_i <- W_i / Σ_{j≠i} n_ij / (p_i + p_j)
    返回归一化后的强度(和为 1),越大越强。
    """
    items = sorted({x for pair in pairs for x in pair})
    idx = {name: i for i, name in enumerate(items)}
    n = len(items)
    wins = np.zeros(n)
    counts = np.zeros((n, n))
    for w, l in pairs:
        wins[idx[w]] += 1
        counts[idx[w], idx[l]] += 1
        counts[idx[l], idx[w]] += 1

    p = np.ones(n)
    for _ in range(iters):
        new = np.empty(n)
        for i in range(n):
            denom = sum(
                counts[i, j] / (p[i] + p[j])
                for j in range(n)
                if j != i and counts[i, j] > 0
            )
            new[i] = wins[i] / denom if denom > 0 else p[i]
        new = np.maximum(new, 1e-12)
        new /= new.sum()
        if np.allclose(new, p, atol=1e-12):
            p = new
            break
        p = new
    return {name: float(p[idx[name]]) for name in items}


def bootstrap_ci(
    per_query_scores: Sequence[float],
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> Tuple[float, float, float]:
    """按 **query** 重采样求均值的置信区间。

    重点:重采样单位必须是 query,不是 (query, result) 对 —— 同一 query 下的
    多个结果高度相关,按对重采样会把置信区间算得过窄。
    返回 (mean, lo, hi)。
    """
    x = np.asarray(per_query_scores, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.array(
        [rng.choice(x, size=len(x), replace=True).mean() for _ in range(n_boot)]
    )
    return (
        float(x.mean()),
        float(np.quantile(means, alpha / 2)),
        float(np.quantile(means, 1 - alpha / 2)),
    )


def stratified_agreement(
    judge: Sequence, human: Sequence, difficulty: Sequence[str]
) -> Dict[str, dict]:
    """按难度分层报告一致率 —— 整体数字会掩盖困难样本上的崩塌。"""
    out = {}
    for level in sorted(set(difficulty)):
        j = [x for x, d in zip(judge, difficulty) if d == level]
        h = [x for x, d in zip(human, difficulty) if d == level]
        out[level] = {
            "n": len(j),
            "agreement": raw_agreement(j, h),
            "kappa": cohens_kappa(j, h),
        }
    out["overall"] = {
        "n": len(judge),
        "agreement": raw_agreement(judge, human),
        "kappa": cohens_kappa(judge, human),
    }
    return out


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _tests():
    # --- kappa 基本性质 ---
    a = ["rel", "rel", "irr", "irr"]
    assert raw_agreement(a, a) == 1.0 and abs(cohens_kappa(a, a) - 1.0) < 1e-12
    # 完全相反 -> kappa 为 -1
    opp = ["irr", "irr", "rel", "rel"]
    assert abs(cohens_kappa(a, opp) + 1.0) < 1e-12
    # 常数标注者 -> p_e = 1 -> 定义为 0
    assert cohens_kappa(["rel"] * 4, ["rel"] * 4) == 0.0

    # --- kappa 揭穿「高 raw agreement」的假象 ---
    # 95% 的样本是 irrelevant;judge 全判 irrelevant
    human = ["irr"] * 95 + ["rel"] * 5
    lazy = ["irr"] * 100
    assert abs(raw_agreement(lazy, human) - 0.95) < 1e-12
    assert cohens_kappa(lazy, human) == 0.0, "全判一个类别的 judge kappa 必须为 0"

    # --- 位置偏差 ---
    fwd = ["A", "A", "B", "A", "B"]
    perfect = ["B", "B", "A", "B", "A"]  # 完全自洽
    assert position_bias_rate(fwd, perfect) == 0.0
    always_first = ["A", "A", "A", "A", "A"]  # 永远选第一个 -> 严重偏差
    rate = position_bias_rate(fwd, always_first)
    assert rate > 0.5, rate
    agg = debias_pairwise(fwd, perfect)
    assert agg == ["first", "first", "second", "first", "second"]
    assert debias_pairwise(["A"], ["A"]) == ["tie"]  # 不自洽记平局

    # --- Bradley-Terry 能恢复真实排序 ---
    rng = np.random.default_rng(0)
    truth = {"sys_a": 0.6, "sys_b": 0.3, "sys_c": 0.1}
    names = list(truth)
    pairs = []
    for _ in range(3000):
        i, j = rng.choice(len(names), size=2, replace=False)
        ni, nj = names[i], names[j]
        p = truth[ni] / (truth[ni] + truth[nj])
        pairs.append((ni, nj) if rng.random() < p else (nj, ni))
    fit = bradley_terry(pairs)
    order = sorted(fit, key=lambda k: -fit[k])
    assert order == ["sys_a", "sys_b", "sys_c"], (order, fit)
    for n in names:
        assert abs(fit[n] - truth[n]) < 0.08, (n, fit[n], truth[n])

    # --- bootstrap CI ---
    scores = list(rng.normal(0.72, 0.15, size=200))
    mean, lo, hi = bootstrap_ci(scores)
    assert lo < mean < hi and (hi - lo) < 0.12
    # 样本越少区间越宽
    _, lo2, hi2 = bootstrap_ci(scores[:20])
    assert (hi2 - lo2) > (hi - lo)

    # --- 分层报告 ---
    # 模仿 Exa 报的 easy 97% / hard 83%
    j = ["rel"] * 97 + ["irr"] * 3 + ["rel"] * 83 + ["irr"] * 17
    h = ["rel"] * 100 + ["rel"] * 100
    diff = ["easy"] * 100 + ["hard"] * 100
    rep = stratified_agreement(j, h, diff)
    assert abs(rep["easy"]["agreement"] - 0.97) < 1e-9
    assert abs(rep["hard"]["agreement"] - 0.83) < 1e-9
    assert abs(rep["overall"]["agreement"] - 0.90) < 1e-9

    print("  全部断言通过\n")
    print("  懒惰 judge(全判 irrelevant,类别 95/5 不平衡):")
    print(
        "    raw agreement = {:.2f}   kappa = {:.2f}   <- kappa 揭穿了它".format(
            raw_agreement(lazy, human), cohens_kappa(lazy, human)
        )
    )
    print("\n  分层一致率(模仿 evals-at-exa 报的 easy/hard):")
    for lvl in ("easy", "hard", "overall"):
        r = rep[lvl]
        print("    {:<8} n={:<5} agreement={:.2f}".format(lvl, r["n"], r["agreement"]))
    print("    -> 整体 0.90 完全掩盖了困难样本上的 0.83")
    print(
        "\n  Bradley-Terry 拟合: "
        + ", ".join("{}={:.3f}(真值 {:.2f})".format(k, fit[k], truth[k]) for k in names)
    )
    m, lo_, hi_ = bootstrap_ci(scores)
    print("  Bootstrap: mean={:.3f}  95% CI=[{:.3f}, {:.3f}]".format(m, lo_, hi_))


if __name__ == "__main__":
    print("Drill D · LLM judge 一致率与系统对比")
    _tests()
    print("""
面试追问预演:
  Q 为什么不能只报 agreement?
  A 类别不平衡时它会骗人。一个「全判不相关」的 judge 在 95/5 的数据上
    agreement 有 0.95,但 kappa 是 0 —— 它没有任何判别力。

  Q pointwise 还是 pairwise?
  A pairwise 理论上更可靠(人更擅长比较而非打绝对分),但成本是 O(n²) 且
    只给相对序、拿不到绝对分,难以跨时间追踪。pointwise 是 O(n)、可缓存、
    可以直接喂给 nDCG。Exa 就是知道 pairwise 更优仍默认 pointwise,
    这是个明确的工程取舍 —— 面试里能说出「他们知道但仍这么选」很加分。

  Q 位置偏差怎么处理?
  A 双向判定:交换顺序再问一次,只有两次自洽才采信,不一致记平局。
    代价是 judge 调用翻倍。也可以在 prompt 里要求先给理由再给结论,
    以及随机化呈现顺序后统计整体胜率。

  Q judge 本身怎么验证?
  A 用人类标注的校准集,分层报 agreement 和 kappa;定期重跑防止模型
    版本漂移。judge 换版本要当作一次「实验变量变更」,不能悄悄升级 ——
    否则历史指标不可比。

  Q 系统 A 比 B 高 2 个点,能上线吗?
  A 先看置信区间,而且 bootstrap 的重采样单位必须是 query 而不是
    (query,result) 对 —— 同 query 内的结果高度相关,按对采样会让区间
    虚假地变窄。再看分层:是全面提升还是只在简单 query 上提升。
""")
```




## drill_e_streaming_quantile.py

```python
"""Drill E · 流式分位数:桶压缩、相对误差、可合并 sketch

⏱ timebox 25 分钟  ｜  概率评级:★★★★★(**这题 Exa 真考过**)

为什么是这道题:2026-07-28 Exa 第一轮技术面的实际题目——
「给一个 stream,怎么返回任意 percentile」。
推导路线:全排序 -> 压缩空间 -> 分桶 -> 引入误差容忍 -> **log 分桶**。
这就是 DDSketch。

搜索系统里到处都是这个东西:p50/p99 延迟监控、召回分数分布、
每查询成本分布。而且 agent 会连着搜 5~30 次,尾延迟被放大
(单次 p99=1% -> 30 次里至少撞一次的概率 1-0.99^30 ≈ 26%),
所以「分位数怎么算」在 agentic search 里不是运维小事。

冷写协议:
    cp drill_e_streaming_quantile.py scratch.py  -> 删实现体 -> 计时 25 分钟

面试时必须能顺口说出来的四句:
    1. 延迟跨几个数量级,所以要的是**相对误差**(p99 误差 1%)而不是
       绝对误差(误差 1ms)。-> 桶宽随值指数增长 -> log 分桶
    2. 桶索引就是 i = ceil( log(x) / log(gamma) ),gamma = (1+a)/(1-a)
    3. 桶数 = ln(max/min) / ln(gamma)。a=1%、值域 1ms~100s -> **约 575 个桶**
       (不到 5KB) 就能覆盖全部延迟,这就是「压缩空间」的答案
    4. **必须可合并(mergeable)**:每台机器一个 sketch,中心节点相加。
       百分位数本身不能跨机平均,sketch 可以。分布式监控里这是硬需求
"""

import math
import random

# ==========================================================================
# COLD-WRITE ZONE 开始
# ==========================================================================


def exact_quantile(values, q: float) -> float:
    """参考实现:全排序取第 ceil(q*(n-1)) 个(0-indexed,nearest-rank 风格)。

    O(n) 空间、O(n log n) 时间 —— 面试里先写这个,再说为什么不够。
    """
    if not values:
        raise ValueError("空流没有分位数")
    s = sorted(values)
    rank = math.ceil(q * (len(s) - 1))
    return s[rank]


class FixedBucketSketch:
    """固定宽度分桶 —— 「压缩空间」的第一版,也是用来暴露问题的对照组。

    桶数 = 值域 / 宽度。想在 1ms 处也有 1ms 精度,又要覆盖到 100s,
    就需要 100_000 个桶。**绝对误差恒定 = 小值处相对误差爆炸**。
    """

    def __init__(self, width: float):
        self.width = width
        self.buckets = {}
        self.count = 0

    def add(self, x: float) -> None:
        i = int(x // self.width)
        self.buckets[i] = self.buckets.get(i, 0) + 1
        self.count += 1

    def quantile(self, q: float) -> float:
        rank = math.ceil(q * (self.count - 1))
        cum = 0
        for i in sorted(self.buckets):
            cum += self.buckets[i]
            if cum > rank:
                return (i + 0.5) * self.width  # 桶中点
        raise ValueError("不该到这里")

    def n_buckets(self) -> int:
        return len(self.buckets)


class DDSketch:
    """log 分桶,保证**相对误差** <= alpha,且可合并。

    桶 i 覆盖区间 (gamma^(i-1), gamma^i],代表值取 2*gamma^i / (gamma+1)。
    这个代表值让区间两端的相对误差相等,都正好是 alpha:
        右端 x=gamma^i    : 1 - 2/(gamma+1)     = (gamma-1)/(gamma+1) = alpha
        左端 x=gamma^(i-1): 2*gamma/(gamma+1)-1 = (gamma-1)/(gamma+1) = alpha
    所以 gamma = (1+alpha)/(1-alpha) 不是凑出来的,是解出来的。
    """

    def __init__(self, alpha: float = 0.01):
        if not 0 < alpha < 1:
            raise ValueError("alpha 必须在 (0,1)")
        self.alpha = alpha
        self.gamma = (1 + alpha) / (1 - alpha)
        self.log_gamma = math.log(self.gamma)
        self.buckets = {}  # 桶索引 -> 计数
        self.zero_count = 0  # 0 不能取 log,单独记
        self.count = 0

    # ---- 写入 ----------------------------------------------------------
    def _index(self, x: float) -> int:
        return math.ceil(math.log(x) / self.log_gamma)

    def add(self, x: float) -> None:
        if x < 0:
            # 负值要用一组镜像桶。延迟/分数都非负,面试里说明这个假设即可。
            raise ValueError("这一版只处理非负值")
        self.count += 1
        if x == 0.0:
            self.zero_count += 1
            return
        i = self._index(x)
        self.buckets[i] = self.buckets.get(i, 0) + 1

    # ---- 查询 ----------------------------------------------------------
    def _value(self, i: int) -> float:
        return 2.0 * self.gamma**i / (self.gamma + 1.0)

    def quantile(self, q: float) -> float:
        """返回 x~,保证 |x~ - x_q| <= alpha * x_q,x_q 是真实的第 q 分位元素。

        桶内计数是精确的,所以「累计计数跨过 rank 的那个桶」
        **就是**真实第 q 分位元素所在的桶 —— 误差只来自桶内取代表值。
        """
        if self.count == 0:
            raise ValueError("空 sketch")
        rank = math.ceil(q * (self.count - 1))
        if rank < self.zero_count:
            return 0.0
        cum = self.zero_count
        for i in sorted(self.buckets):
            cum += self.buckets[i]
            if cum > rank:
                return self._value(i)
        return self._value(max(self.buckets))

    # ---- 合并 ----------------------------------------------------------
    def merge(self, other: "DDSketch") -> "DDSketch":
        """桶索引只由 (alpha, x) 决定,与插入顺序和数据划分无关
        -> 同 alpha 的两个 sketch 直接逐桶相加。这是分布式聚合的全部秘密。"""
        if abs(other.alpha - self.alpha) > 1e-12:
            raise ValueError("alpha 不同的 sketch 不能合并")
        out = DDSketch(self.alpha)
        out.buckets = dict(self.buckets)
        for i, c in other.buckets.items():
            out.buckets[i] = out.buckets.get(i, 0) + c
        out.zero_count = self.zero_count + other.zero_count
        out.count = self.count + other.count
        return out

    # ---- 空间 ----------------------------------------------------------
    def n_buckets(self) -> int:
        return len(self.buckets) + (1 if self.zero_count else 0)

    def bucket_bound(self, lo: float, hi: float) -> int:
        """理论桶数上界:覆盖 [lo, hi] 需要 ln(hi/lo) / ln(gamma) 个桶。
        **这是「压缩空间」那一问的定量答案。**"""
        return math.ceil(math.log(hi / lo) / self.log_gamma)


# ==========================================================================
# COLD-WRITE ZONE 结束
# ==========================================================================


def _latency_stream(n: int, seed: int = 0):
    """模拟真实延迟:对数正态主体 + 1% 的长尾。跨约 4 个数量级。"""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        if rng.random() < 0.01:
            out.append(rng.lognormvariate(math.log(2000), 0.8))  # 尾:~2s
        else:
            out.append(rng.lognormvariate(math.log(30), 0.7))  # 主体:~30ms
    return out


def _check():
    N = 200_000
    xs = _latency_stream(N)
    qs = [0.5, 0.9, 0.99, 0.999]

    # ---- 1. DDSketch 的相对误差保证 ----
    alpha = 0.01
    dd = DDSketch(alpha)
    for x in xs:
        dd.add(x)

    print("q       exact       DDSketch    相对误差")
    for q in qs:
        e = exact_quantile(xs, q)
        a = dd.quantile(q)
        rel = abs(a - e) / e
        print("{:<7} {:>10.3f}  {:>10.3f}  {:>8.4%}".format(q, e, a, rel))
        # 1.001 的余量给浮点 log 在桶边界上的抖动
        assert rel <= alpha * 1.001, "q={} 相对误差 {:.4%} 超过 alpha".format(q, rel)

    # ---- 2. 空间:log 桶 vs 固定桶 ----
    fixed = FixedBucketSketch(width=1.0)  # 1ms 宽,才能在小值处有精度
    for x in xs:
        fixed.add(x)
    print("\n空间对比({} 个样本,值域 {:.1f} ~ {:.1f} ms)".format(N, min(xs), max(xs)))
    print("  全排序               : {:>7} 个数".format(N))
    print("  固定桶(1ms,实际占用) : {:>7} 个桶".format(fixed.n_buckets()))
    print("  DDSketch(1%,实际占用): {:>7} 个桶".format(dd.n_buckets()))
    print("  —— 最坏情况(覆盖 1ms~100s 全值域,不靠数据稀疏)——")
    print("  固定桶(1ms)          : {:>7} 个桶".format(100_000))
    print("  DDSketch(1%)         : {:>7} 个桶".format(dd.bucket_bound(1.0, 100_000.0)))
    # 注意:两者都用 dict 稀疏存储,所以实测差距(~4x)远小于最坏情况差距(~170x)。
    # 真正的结论是**最坏情况有界**:固定桶的桶数随值域线性增长、无上界可言,
    # log 桶随值域**对数**增长。稀疏性只是掩盖了这一点。
    assert dd.n_buckets() < fixed.n_buckets(), "占用桶数 log 桶也应更少"
    assert dd.bucket_bound(1.0, 100_000.0) < 100_000 / 100, (
        "最坏情况下 log 桶应该省两个数量级"
    )

    # ---- 3. 固定桶在小值处相对误差爆炸(这是它被淘汰的原因) ----
    tiny = [0.08, 0.12, 0.2, 0.35, 0.6]  # 亚毫秒:全落进固定桶的第 0 桶
    f2 = FixedBucketSketch(width=1.0)
    d2 = DDSketch(alpha)
    for x in tiny:
        f2.add(x)
        d2.add(x)
    ex = exact_quantile(tiny, 0.5)
    rel_fixed = abs(f2.quantile(0.5) - ex) / ex
    rel_dd = abs(d2.quantile(0.5) - ex) / ex
    print("\n亚毫秒区间的 p50(exact={:.2f})".format(ex))
    print("  固定桶相对误差: {:.1%}".format(rel_fixed))
    print("  DDSketch      : {:.3%}".format(rel_dd))
    assert rel_fixed > 0.1 and rel_dd <= alpha * 1.001

    # ---- 4. 可合并:分片后合并 == 一次性灌入 ----
    shards = [DDSketch(alpha) for _ in range(4)]
    for j, x in enumerate(xs):
        shards[j % 4].add(x)
    merged = shards[0]
    for s in shards[1:]:
        merged = merged.merge(s)
    assert merged.count == dd.count
    for q in qs:
        assert merged.quantile(q) == dd.quantile(q), "合并必须与整体一致"
    print("\n4 分片合并 == 单机整体:全部分位数逐一相等 ✓")

    # ---- 5. 平均值不能替代分位数(顺带反驳一个常见提议) ----
    shard_p99 = [s.quantile(0.99) for s in shards]
    avg_of_p99 = sum(shard_p99) / len(shard_p99)
    true_p99 = exact_quantile(xs, 0.99)
    print(
        "\n把各分片 p99 直接平均 = {:.1f},真 p99 = {:.1f},偏差 {:.1%}".format(
            avg_of_p99, true_p99, abs(avg_of_p99 - true_p99) / true_p99
        )
    )
    print(
        "(这里分片是随机均分所以还算接近;按机器/地域分片时会差很多"
        " —— 所以要合并 sketch,不是平均分位数)"
    )

    print("\nDrill E 全部断言通过")


if __name__ == "__main__":
    _check()
    print("""
================ 面试追问预演 ================
Q: 为什么不用 reservoir sampling?
A: 可以,而且实现更简单、支持任意分位数和其他统计量。但它的误差是**采样误差**,
   在 p99.9 这种极尾部,样本里可能只有几个点 -> 方差极大。
   DDSketch 对每个分位数都给**确定性**的相对误差上界,尾部同样成立。
   要 p999 的稳定值就用 sketch,要灵活的探索性分析就用 reservoir。

Q: t-digest 呢?
A: 同类工具。t-digest 用可变大小的质心,**尾部精度高、中位数附近相对松**,
   而且误差是经验性的、没有 DDSketch 那样的严格相对误差保证。
   合并 t-digest 还需要重新压缩质心,不是简单相加。
   选型:要严格 SLO 保证 -> DDSketch;要固定内存上限 -> t-digest。

Q: 桶会无限增长吗?
A: 理论上界是 ln(max/min)/ln(gamma),对延迟这种有物理上下界的量是有界的
   (1%误差、1ms~100s 只要约 575 个桶)。真要硬上限,就设 max_bins,
   超了把最小的几个桶折叠进一个「下溢桶」—— 牺牲小值精度换固定内存,
   对延迟监控完全可接受,因为你关心的是尾部。

Q: 怎么做滑动窗口(只要最近 5 分钟)?
A: 分桶时间片:每分钟一个 sketch,查询时合并最近 5 个,过期的丢掉。
   **可合并性在这里第二次救场** —— 这就是为什么 mergeable 是硬需求而不是加分项。

Q: 并发写怎么办?
A: 每线程一个 sketch,查询时合并(第三次)。桶是纯计数,无锁累加也行。
   这比对一个共享结构加锁快得多,也是 sketch 相对「保留全部样本」的
   另一个工程优势。

Q: 这跟 Exa 有什么关系?
A: ① 搜索的 SLO 是 p99 不是均值,agent 连搜 30 次会把尾延迟放大到 26% 的
     任务受影响;② 多路索引赛跑 = hedged request,是用算力换 p99,
     要不要 hedge 得先能准确量 p99;③ 相同的结构也用来监控召回分数分布和
     每查询成本分布的漂移。
""")
```




## run_all.py

```python
#!/usr/bin/env python3
"""跑四个 Exa drill 的参考实现（全部自带断言）。

用法:  python3 run_all.py

会优先用 interview/.venv 的 python(带 torch);找不到就用当前解释器,
此时 drill C 会被跳过并提示。
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = "/Users/mingrui/Documents/codes/interview/.venv/bin/python"

DRILLS = [
    ("A · 检索评测指标", "drill_a_retrieval_metrics.py", False),
    ("B · 向量检索 / Matryoshka", "drill_b_vector_search.py", False),
    ("C · PyTorch InfoNCE", "drill_c_infonce_pytorch.py", True),  # 需要 torch
    ("D · Judge 一致率", "drill_d_judge_agreement.py", False),
    ("E · 流式分位数 / DDSketch", "drill_e_streaming_quantile.py", False),
]


def has_torch(python: str) -> bool:
    return (
        subprocess.run([python, "-c", "import torch"], capture_output=True).returncode
        == 0
    )


def main() -> int:
    python = VENV if os.path.exists(VENV) else sys.executable
    torch_ok = has_torch(python)
    print("解释器: {}\ntorch: {}\n".format(python, "可用" if torch_ok else "不可用"))

    failed, skipped = [], []
    for title, script, needs_torch in DRILLS:
        if needs_torch and not torch_ok:
            skipped.append(title)
            continue
        print("=" * 70)
        print(title)
        print("=" * 70)
        proc = subprocess.run(
            [python, script], cwd=HERE, capture_output=True, text=True
        )
        # 只打印断言结果那几行,不刷屏追问预演
        for line in proc.stdout.splitlines():
            if "面试追问预演" in line:
                break
            print(line)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr)
            failed.append(title)
        print()

    print("=" * 70)
    if skipped:
        print("跳过(缺 torch): " + ", ".join(skipped))
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    print("{} 个 drill 全部通过".format(len(DRILLS) - len(skipped)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/labs/exa_drills/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/exa_drills/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
