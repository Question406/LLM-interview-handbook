---
id: drustz-b864269bf79db3f8f0
section: labs
order: 18
level: A
title: Lab 03 · InfoNCE、假负例陷阱、Matryoshka 级联成本
quick: 作者完整文档 · Lab 03 · InfoNCE、假负例陷阱、Matryoshka 级联成本
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab03_retrieval_negatives/README.md
    type: primary
---
# Lab 03 · InfoNCE、假负例陷阱、Matryoshka 级联成本

⏱ 40 分钟（砍时:只跑 `solution.py`，10 分钟）｜ 安排在 **Day 2 下午**（Exa 对口）

对口 [06 §五/§六/§九](?book=drustz-interview-2026&section=mlsd&question=drustz-ffab78b0379e3934e2) 与 [13 · Exa 卡](?book=drustz-interview-2026&section=mlsd&question=drustz-8542776e5697e93de9)。

## 怎么做

```bash
python3 solution.py      # 四部分演示，0.3 秒
python3 test_solution.py # 10 条断言，全绿
```



## 四个实测结论

### A. 为什么必须换 hard negative（不是"因为大家都这么做"）

```text
easy/random   loss=0.0003   |grad|=0.0046
hard          loss=0.4303   |grad|=1.8985      <- 梯度差 400 倍
```



模型早就能把无关文档分开，easy negative 的 loss 和梯度都趋近 0，**再训是在做无用功**。这才是换 negative 的真正理由。

### B. 假负例陷阱（本 lab 的题眼）

语料里有一个 `unlabeled_relevant`：和正例讲同一件事、同样相关，但**标注集里没有它**。

```text
dot(positive, unlabeled_relevant) = 0.910
max dot(positive, hard_neg_*)     = 0.716

训练前  unlabeled_relevant 排名 = 2
朴素挖 top-6 hard negatives     = [unlabeled_relevant, hard_neg_4, ...]   <- 污染
训练后  unlabeled_relevant 排名 = 4                                        <- 被推走
```



你以为在做 hard negative mining，实际上在**系统性地把自己的正例训练成负例**。

这正是 Exa 在 [evals-at-exa](https://exa.ai/blog/evals-at-exa) 里放弃 MS Marco 式封闭评测的**第一个理由：稀疏标注导致假负例**。训练侧和评测侧是同一个病。

### C. 去噪：一个 tau 的差别

规则：`dot(candidate, positive) > tau` 就跳过——**与已知正例极其相似的候选，大概率本身就是正例，只是没被标注**。

关键是这条规则**不需要知道谁是假负例**，只看候选与正例的相似度。它之所以可用，是因为假负例与正例的相似度（0.910）显著高于真负例（≤0.716）——测试 `test_denoise_tau_separates_false_negative_from_true_hard_negatives` 就在断言这个前提。

```text
去噪后 top-6 = [hard_neg_4, hard_neg_0, ...]   （unlabeled_relevant 被排除）
训练后  unlabeled_relevant 排名 = 2             <- 保住了

对照：污染=4   去噪=2
```



### D. Matryoshka 级联的可算权衡（2012 文档 / 64 维）

```text
coarse_dim  shortlist   recall@10   成本
64          10          1.00        100% of full
32          50          1.00         52%
16          50          1.00         27%        <- 1/4 维，召回不掉
 8          50          0.80         15%        <- 开始掉
 8         200          1.00         22%        <- 加大 shortlist 买回来了
 4          50          0.00          9%        <- 截过头，崩溃
 4         200          0.60         16%
```



三个可以直接说的结论：
1. **降维省的是全库扫描成本**，`N × m` 里 N 很大，所以 m 的每一点都很值钱；
2. **精排贵但只碰 top-k**，所以加大 shortlist 是便宜的补救——`m=8, k=200` 用 22% 的成本拿回了满召回；
3. 但截过头（1/16 维）任何 shortlist 都救不回来，信息已经在粗筛阶段丢了。

这就是 Exa 把 2048 维截到 **256 维（1/8）省 20× 内存**的同一个权衡。面试里能把这条曲线画出来，比背"我们用 Matryoshka"强得多。

## 追问预演

- **「in-batch negatives 够不够？」** 训练初期够（便宜、batch 越大越好），后期必须换成从索引里挖的 hard negatives。工程上还要注意跨设备收集 in-batch negatives（GradCache 之类），否则大 batch 放不下。
- **「hard negative 从哪挖？」** BM25 的 top-k 非相关、上一版模型的 top-k 非相关（ANCE 式迭代，每隔若干步刷新索引）。挖完必须去噪，见 C。
- **「除了 tau 还有什么去噪法？」** 用 cross-encoder teacher 给候选打分，分数过高的剔除或改成 soft label；或者保留多正例（multi-positive）而不是强行二分。
- **「temperature 怎么选？」** 太小 → softmax 饱和、梯度消失（本 lab 里 T=0.05 时 loss 就已经趋近 0）；太大 → 区分不出 hard 和 easy。要在 dev set 上扫。
- **「离线 recall 提升了，线上没动，为什么？」** 训练时的候选分布必须接近线上第一阶段召回器的输出分布，否则 offline gain 不迁移。见 [03 §4](?book=drustz-interview-2026&section=mlsd&question=drustz-c7127e4b503f4848b2)。

## solution.py

```python
"""Lab 03 · InfoNCE、hard negative 的 false-negative 陷阱、Matryoshka 级联成本

对口 06_search_post_training.md §五/§六/§九,以及 13_company_cards.md 的 Exa 卡。
纯标准库、确定性(md5 生成向量,不受 PYTHONHASHSEED 影响)。

四个可以直接带进面试的结论:
  1. easy/random negative 到后期 loss 和梯度都趋近 0,模型学不到东西;
     hard negative 才有信号 —— 这是要换 negative 的真正原因。
  2. 但 top-k 里混着**未标注的相关文档**。把它们当负例训练,会把真正相关的
     文档推走。这正是 Exa 放弃 MS Marco 式封闭评测的第一个理由:
     稀疏标注 -> 假负例。
  3. 去噪规则要**可解释且不偷看答案**:与已知正例过于相似的候选,大概率
     本身就是正例,不当负例。
  4. Matryoshka 截断维度粗筛 + 全维精排,recall 与成本的权衡是可算的;
     shortlist 变大可以买回一部分被截断损失的召回,而且很便宜。
"""

import hashlib
import math
from typing import Dict, List, Sequence, Tuple

DIM = 16  # A/B/C 用的小语料维度
TEMPERATURE = 0.10
DENOISE_TAU = 0.75  # 与正例相似度高于此值的候选不做负例(应在 dev set 上调)


# --------------------------------------------------------------------------
# 确定性向量工具
# --------------------------------------------------------------------------


def _unit(vec: List[float]) -> List[float]:
    n = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / n for v in vec]


def _seeded_vec(name: str, dim: int = DIM) -> List[float]:
    out = []
    for i in range(dim):
        h = hashlib.md5("{}::{}".format(name, i).encode()).hexdigest()
        out.append(int(h[:8], 16) / 0xFFFFFFFF - 0.5)
    return _unit(out)


def _blend(a: Sequence[float], b: Sequence[float], w: float) -> List[float]:
    return _unit([(1 - w) * x + w * y for x, y in zip(a, b)])


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def truncated_dot(a: Sequence[float], b: Sequence[float], m: int) -> float:
    """只用前 m 维打分 —— Matryoshka 粗筛就是这么做的。"""
    return sum(a[i] * b[i] for i in range(m))


# --------------------------------------------------------------------------
# InfoNCE
# --------------------------------------------------------------------------


def softmax(scores: Sequence[float]) -> List[float]:
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    z = sum(exps)
    return [e / z for e in exps]


def infonce_loss(q, positive, negatives, temperature: float = TEMPERATURE) -> float:
    """L = -log( exp(s+/T) / (exp(s+/T) + Σ exp(s-/T)) )"""
    scores = [dot(q, positive) / temperature]
    scores += [dot(q, n) / temperature for n in negatives]
    return -math.log(softmax(scores)[0])


def infonce_grad(q, positive, negatives, temperature: float = TEMPERATURE):
    """∂L/∂q = ( Σ_i p_i·d_i - d+ ) / T。

    直觉:把 q 拉向正例,推离**当前得分高**的候选。
    负例越 hard,它在 softmax 里的权重越大,梯度越强。
    """
    docs = [positive] + list(negatives)
    probs = softmax([dot(q, d) / temperature for d in docs])
    grad = [0.0] * len(q)
    for p, d in zip(probs, docs):
        for i in range(len(q)):
            grad[i] += p * d[i]
    return [(grad[i] - positive[i]) / temperature for i in range(len(q))]


def train_query(
    q0,
    positive,
    negatives,
    steps: int = 150,
    lr: float = 0.05,
    temperature: float = TEMPERATURE,
) -> List[float]:
    """对 query 向量做梯度下降。真实系统更新的是 encoder 参数,机制相同。"""
    q = list(q0)
    for _ in range(steps):
        g = infonce_grad(q, positive, negatives, temperature)
        q = _unit([qi - lr * gi for qi, gi in zip(q, g)])
    return q


# --------------------------------------------------------------------------
# 小语料:一个 query、一个已标注正例、一个未标注但相关的文档、一批负例
# --------------------------------------------------------------------------


def build_corpus() -> Tuple[List[float], Dict[str, List[float]]]:
    topic = _seeded_vec("topic:transformer-attention")
    other = _seeded_vec("topic:database-indexing")

    query = _blend(topic, _seeded_vec("q-noise"), 0.15)
    positive = _blend(topic, _seeded_vec("d-pos"), 0.40)

    docs: Dict[str, List[float]] = {"labeled_positive": positive}
    # 与正例讲同一件事、同样相关,但标注集里没有它 —— 假负例的真实来源
    docs["unlabeled_relevant"] = _blend(positive, _seeded_vec("d-unlab"), 0.30)
    # 主题相邻但确实不相关
    for i in range(8):
        docs["hard_neg_{}".format(i)] = _blend(
            topic, _seeded_vec("hn{}".format(i)), 0.52 + 0.01 * i
        )
    # 完全无关
    for i in range(6):
        docs["easy_neg_{}".format(i)] = _blend(
            other, _seeded_vec("d-easy-{}".format(i)), 0.5
        )
    return query, docs


def rank_of(query, docs: Dict[str, List[float]], doc_id: str) -> int:
    """1 = 最相关。"""
    return sorted(docs, key=lambda d: -dot(query, docs[d])).index(doc_id) + 1


def mine_hard_negatives(
    query, docs, positive_id: str, top_k: int = 6, denoise_tau: float = None
) -> List[str]:
    """用当前模型取 top-k 非正例作为 hard negatives(ANCE 式迭代挖掘)。

    denoise_tau: 丢弃与正例相似度 > tau 的候选。
        依据:「与已知正例极其相似的文档,大概率本身就是正例,只是没被标注」。
        注意这条规则只看 (候选, 正例) 的相似度,**不需要知道谁是假负例**。
    """
    pos_vec = docs[positive_id]
    ranked = sorted(
        (d for d in docs if d != positive_id), key=lambda d: -dot(query, docs[d])
    )
    picked = []
    for d in ranked:
        if denoise_tau is not None and dot(docs[d], pos_vec) > denoise_tau:
            continue
        picked.append(d)
        if len(picked) == top_k:
            break
    return picked


# --------------------------------------------------------------------------
# Matryoshka 级联(独立的大语料)
# --------------------------------------------------------------------------

LARGE_DIM = 64
LARGE_N = 2000
N_GOLD = 12


def build_large_corpus():
    topic = _seeded_vec("topic:gold", LARGE_DIM)
    query = _blend(topic, _seeded_vec("qn", LARGE_DIM), 0.10)
    docs = {}
    for i in range(N_GOLD):
        docs["gold_{}".format(i)] = _blend(
            topic, _seeded_vec("g{}".format(i), LARGE_DIM), 0.30 + 0.02 * i
        )
    for i in range(LARGE_N):
        docs["d{}".format(i)] = _blend(
            _seeded_vec("t{}".format(i % 40), LARGE_DIM),
            _seeded_vec("n{}".format(i), LARGE_DIM),
            0.5,
        )
    gold = [k for k in docs if k.startswith("gold_")]
    return query, docs, gold


def cascade(
    query, docs, gold, coarse_dim: int, shortlist_k: int, final_k: int = 10
) -> Tuple[float, int]:
    """前 coarse_dim 维全库粗筛 -> top-k 用全维精排 -> 取 final_k。

    成本按乘加次数计: N*coarse_dim + shortlist_k*LARGE_DIM。
    """
    coarse = sorted(docs, key=lambda d: -truncated_dot(query, docs[d], coarse_dim))
    shortlist = coarse[:shortlist_k]
    final = sorted(shortlist, key=lambda d: -dot(query, docs[d]))[:final_k]
    gold_set = set(gold)
    recall = len([d for d in final if d in gold_set]) / float(final_k)
    cost = len(docs) * coarse_dim + shortlist_k * LARGE_DIM
    return recall, cost


def main():
    query, docs = build_corpus()
    pos_id, unlab_id = "labeled_positive", "unlabeled_relevant"

    print("=" * 76)
    print("A · hard negative vs random negative:梯度信号强度")
    print("=" * 76)
    easy = [docs[d] for d in sorted(docs) if d.startswith("easy_neg")][:6]
    hard = [docs[d] for d in sorted(docs) if d.startswith("hard_neg")][:6]
    for name, negs in (("easy/random", easy), ("hard", hard)):
        loss = infonce_loss(query, docs[pos_id], negs)
        g = infonce_grad(query, docs[pos_id], negs)
        gnorm = math.sqrt(sum(x * x for x in g))
        print("  {:<12} loss={:.4f}   |grad|={:.4f}".format(name, loss, gnorm))
    print("\n  -> easy negative 的 loss 和梯度都趋近 0:模型已经能轻松区分,再练无益。")
    print(
        "     这才是「in-batch random negatives 到后期必须换 hard negatives」的原因。"
    )

    print("\n" + "=" * 76)
    print("B · false negative 陷阱:把未标注的相关文档当负例")
    print("=" * 76)
    print("  相似度事实:")
    print(
        "     dot(positive, unlabeled_relevant) = {:.3f}".format(
            dot(docs[pos_id], docs[unlab_id])
        )
    )
    print(
        "     max dot(positive, hard_neg_*)     = {:.3f}".format(
            max(dot(docs[pos_id], docs[d]) for d in docs if d.startswith("hard_neg"))
        )
    )
    print(
        "\n  训练前:  positive 排名={}   unlabeled_relevant 排名={}".format(
            rank_of(query, docs, pos_id), rank_of(query, docs, unlab_id)
        )
    )

    dirty = mine_hard_negatives(query, docs, pos_id, top_k=6)
    print("\n  朴素挖掘 top-6: {}".format(dirty))
    print(
        "  未标注的相关文档被当成负例了吗? {}".format(
            "是 <-- 污染" if unlab_id in dirty else "否"
        )
    )
    q_dirty = train_query(query, docs[pos_id], [docs[d] for d in dirty])
    r_dirty = rank_of(q_dirty, docs, unlab_id)
    print(
        "  训练后:  positive 排名={}   unlabeled_relevant 排名={}  <-- 被推走".format(
            rank_of(q_dirty, docs, pos_id), r_dirty
        )
    )

    print("\n" + "=" * 76)
    print("C · 去噪:与已知正例过于相似的候选,不当负例")
    print("=" * 76)
    print("  规则:dot(candidate, positive) > tau={} 就跳过。".format(DENOISE_TAU))
    print("  注意这条规则不需要知道谁是假负例,只看候选与正例的相似度。")
    clean = mine_hard_negatives(query, docs, pos_id, top_k=6, denoise_tau=DENOISE_TAU)
    print("\n  去噪后 top-6: {}".format(clean))
    q_clean = train_query(query, docs[pos_id], [docs[d] for d in clean])
    r_clean = rank_of(q_clean, docs, unlab_id)
    print(
        "  训练后:  positive 排名={}   unlabeled_relevant 排名={}  <-- 保住了".format(
            rank_of(q_clean, docs, pos_id), r_clean
        )
    )
    print("\n  对照:未标注相关文档的排名  污染={}  去噪={}".format(r_dirty, r_clean))
    print("  -> 同样叫 hard negative mining,一个 tau 的差别决定了你是在提升召回,")
    print("     还是在系统性地把自己的正例训练成负例。")

    print("\n" + "=" * 76)
    print(
        "D · Matryoshka 级联:截断维度粗筛 + 全维精排({} 文档, {} 维)".format(
            LARGE_N + N_GOLD, LARGE_DIM
        )
    )
    print("=" * 76)
    lq, ldocs, lgold = build_large_corpus()
    full_cost = len(ldocs) * LARGE_DIM
    print(
        "  {:<12}{:<12}{:<14}{}".format("coarse_dim", "shortlist", "recall@10", "成本")
    )
    for m, k in [(64, 10), (32, 50), (16, 50), (8, 50), (8, 200), (4, 50), (4, 200)]:
        rec, cost = cascade(lq, ldocs, lgold, m, k)
        print(
            "  {:<12}{:<12}{:<14.2f}{:>8}  ({:>3.0f}% of full)".format(
                m, k, rec, cost, 100.0 * cost / full_cost
            )
        )
    print("\n  -> 截到 1/4 维(16/64)召回不掉而成本只剩 27%;截到 1/8 开始掉;")
    print("     但把 shortlist 从 50 加到 200 能买回一部分 —— 因为精排只作用于 k 条,")
    print("     很便宜。这就是 Exa 把 2048 维截到 256 维省 20x 内存的同一个权衡。")
    print("     面试要点:降维省的是**全库扫描**成本,精排贵但只碰 top-k。")


if __name__ == "__main__":
    main()
```




## test_solution.py

```python
"""Lab 03 测试。跑法: python3 test_solution.py  (也兼容 pytest)"""

import math
import sys

from solution import (
    DENOISE_TAU,
    build_corpus,
    build_large_corpus,
    cascade,
    dot,
    infonce_grad,
    infonce_loss,
    mine_hard_negatives,
    rank_of,
    softmax,
    train_query,
    truncated_dot,
)

POS, UNLAB = "labeled_positive", "unlabeled_relevant"


def _negs(docs, prefix, n):
    return [docs[d] for d in sorted(docs) if d.startswith(prefix)][:n]


def test_softmax_is_a_distribution():
    p = softmax([3.0, 1.0, -2.0, 10.0])
    assert abs(sum(p) - 1.0) < 1e-12
    assert all(x >= 0 for x in p)
    assert p[3] == max(p)


def test_infonce_decreases_when_positive_scores_higher():
    q, docs = build_corpus()
    negs = _negs(docs, "hard_neg", 6)
    loss_before = infonce_loss(q, docs[POS], negs)
    q_after = train_query(q, docs[POS], negs)
    assert infonce_loss(q_after, docs[POS], negs) < loss_before


def test_hard_negatives_carry_more_gradient_than_random():
    """本 lab 的第一个题眼:easy negative 的梯度趋近 0。"""
    q, docs = build_corpus()
    easy, hard = _negs(docs, "easy_neg", 6), _negs(docs, "hard_neg", 6)
    g_easy = infonce_grad(q, docs[POS], easy)
    g_hard = infonce_grad(q, docs[POS], hard)
    n_easy = math.sqrt(sum(x * x for x in g_easy))
    n_hard = math.sqrt(sum(x * x for x in g_hard))
    assert n_hard > 10 * n_easy, (
        "hard 的梯度范数应远大于 easy: {:.4f} vs {:.4f}".format(n_hard, n_easy)
    )
    assert infonce_loss(q, docs[POS], easy) < infonce_loss(q, docs[POS], hard)


def test_naive_mining_picks_up_the_false_negative():
    """未标注但相关的文档会排进 top-k,被当作负例。"""
    q, docs = build_corpus()
    assert UNLAB in mine_hard_negatives(q, docs, POS, top_k=6)


def test_false_negative_contamination_hurts_the_relevant_doc():
    """第二个题眼:污染训练把真正相关的文档推走。"""
    q, docs = build_corpus()
    before = rank_of(q, docs, UNLAB)
    dirty = mine_hard_negatives(q, docs, POS, top_k=6)
    q_dirty = train_query(q, docs[POS], [docs[d] for d in dirty])
    after = rank_of(q_dirty, docs, UNLAB)
    assert after > before, "污染后排名应当变差: {} -> {}".format(before, after)


def test_denoising_protects_the_false_negative():
    """第三个题眼:一个 tau 就能挡住,而且规则不依赖「知道谁是假负例」。"""
    q, docs = build_corpus()
    clean = mine_hard_negatives(q, docs, POS, top_k=6, denoise_tau=DENOISE_TAU)
    assert UNLAB not in clean

    dirty = mine_hard_negatives(q, docs, POS, top_k=6)
    q_dirty = train_query(q, docs[POS], [docs[d] for d in dirty])
    q_clean = train_query(q, docs[POS], [docs[d] for d in clean])
    assert rank_of(q_clean, docs, UNLAB) < rank_of(q_dirty, docs, UNLAB)
    # 去噪不能以牺牲正例为代价
    assert rank_of(q_clean, docs, POS) == 1


def test_denoise_tau_separates_false_negative_from_true_hard_negatives():
    """tau 之所以可用,是因为假负例与正例的相似度显著高于真负例。"""
    _, docs = build_corpus()
    sim_unlab = dot(docs[POS], docs[UNLAB])
    sim_hard_max = max(
        dot(docs[POS], docs[d]) for d in docs if d.startswith("hard_neg")
    )
    assert sim_hard_max < DENOISE_TAU < sim_unlab


def test_truncated_dot_matches_full_dot_at_full_dim():
    _, docs = build_corpus()
    a, b = docs[POS], docs[UNLAB]
    assert abs(truncated_dot(a, b, len(a)) - dot(a, b)) < 1e-12


def test_cascade_trades_recall_for_cost():
    """第四个题眼:截断维度省的是全库成本,但截过头会掉召回。"""
    q, docs, gold = build_large_corpus()
    r_full, c_full = cascade(q, docs, gold, 64, 10)
    r_16, c_16 = cascade(q, docs, gold, 16, 50)
    r_4, c_4 = cascade(q, docs, gold, 4, 50)

    assert r_full == 1.0
    assert r_16 == 1.0 and c_16 < 0.4 * c_full, "1/4 维应当近乎免费"
    assert r_4 < r_16, "截到 1/16 维必须看到召回下降"


def test_bigger_shortlist_buys_back_recall():
    """精排只作用于 k 条,所以加大 shortlist 是便宜的补救。"""
    q, docs, gold = build_large_corpus()
    r_small, c_small = cascade(q, docs, gold, 8, 50)
    r_big, c_big = cascade(q, docs, gold, 8, 200)
    assert r_big > r_small
    assert c_big < 2 * c_small, "加大 shortlist 的成本增幅应当有限"


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print("  PASS  " + t.__name__)
        except AssertionError as e:
            failed += 1
            print("  FAIL  " + t.__name__ + " :: " + str(e))
    print("\n{}/{} passed".format(len(tests) - failed, len(tests)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run())
```

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/labs/lab03_retrieval_negatives/README.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/labs/lab03_retrieval_negatives/README.md)。作者整理资料；许可和第三方来源范围见阅读指南。
