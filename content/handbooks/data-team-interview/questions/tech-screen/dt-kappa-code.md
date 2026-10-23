---
id: dt-kappa-code
section: tech-screen
order: 15
level: A
title: CoderPad：两个人标同一批，Cohen's $\kappa$ 怎么算，低了改什么？
quick: "类别不平衡时偶然一致率本身就很高，所以要报 Cohen's $\\kappa$：先建混淆矩阵，再算 $\\kappa=(p_o-p_e)/(1-p_e)$，$p_o$ 是观测一致率，$p_e$ 是按边际分布算的偶然一致率。$\\kappa$ 低时先改协议和例子，再考虑加人投票。"
companies:
  - apple
tags:
  - Apple
  - CoderPad
  - Annotation
  - Agreement
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "A Coefficient of Agreement for Nominal Scales (Cohen 1960)"
    url: https://journals.sagepub.com/doi/10.1177/001316446002000104
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会报 Cohen's $\kappa$，把偶然一致扣掉，同时把混淆矩阵打出来看分歧在哪；$\kappa$ 低了先改协议和例子，再考虑加人。

原因看一个例子就懂：$p_o=0.9$，但正例占 95%，这时 $p_e$ 已经约 0.9，$\kappa$ 接近 0。两个人一致率 90% 听着不错，可类别这么不平衡，瞎标也能有这么高，这就是「一致率好看、标签没信息」。

按 Cohen 1960 的定义：两名标注员，类别集合 $C$，$n_{ij}$ 是 A 标 $i$、B 标 $j$ 的条数。观测一致率 $p_o=\sum_i n_{ii}/N$；偶然一致率 $p_e=\sum_i p_{i\cdot}p_{\cdot i}$，两个边际都来自这张表。代码就是先数一致，再按两边的类别分布算偶然一致：

```python
from collections import Counter

def cohen_kappa(a_labels, b_labels):
    assert len(a_labels) == len(b_labels) and a_labels
    n = len(a_labels)
    po = sum(x == y for x, y in zip(a_labels, b_labels)) / n
    ca = Counter(a_labels)
    cb = Counter(b_labels)
    cats = set(ca) | set(cb)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in cats)
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return (po - pe) / (1.0 - pe)

def confusion(a_labels, b_labels):
    tab = Counter(zip(a_labels, b_labels))
    cats = sorted(set(a_labels) | set(b_labels))
    return cats, [[tab[(i, j)] for j in cats] for i in cats]
```

一遍计数，$O(N)$，类别数很少，混淆矩阵也就是一张小表。

## 数字怎么解释

报 $\kappa$ 的时候一定带上混淆矩阵。比如 $\kappa=0.4$，但错误全在「部分有用 / 有用」两档，如果这两档的业务含义允许合并，可以改协议后重新标注；错误散在「拒绝 / 遵从」上就不能合并，因为那是安全题。偏好对的 chosen/rejected 也有类似情况：如果 80% 的人总是选更长的那条，高一致率和长度 hack 其实是同一件事，见 `dt-length-hack-data`。

Llama 3 公开写了偏好数据要丢掉「差不多」的对。$\kappa$ 低的那一档，往往说明两个回答太难区分，直接拿去做 DPO 会增加噪声，见 `dt-pref-pair-code`。

还有两个细节。多人标注时用 pairwise $\kappa$ 的中位数，或者用 Fleiss，现场写两人版就够。空标签和跳过不算一个类，除非协议明确把「无法判断」定为合法类，协议怎么写见 `dt-annotator-protocol`。

## 追问

**$\kappa$ 多少才能训？**
没有通用线。安全拒答要很高；开放式有用性 0.4 到 0.6 很常见，靠金标审核来补。报 $\kappa$ 时同时报混淆矩阵。

**$\kappa$ 低了，加人投票行不行？**
三人多数票会把模糊题变成假金标。先修订标注说明，用 20 个争议例子讲清标准，再重新标注。

**和模型 judge 怎么比？**
人与人之间的 $\kappa$ 是协议能达到的上限。人与模型的 $\kappa$ 比这更低，说明 judge 替代不了这一批人工标注，见 `dt-judge-bias`。

**$p_e$ 等于 1 的时候代码怎么处理？**
两个人都只用了同一个类，分母为 0。代码里这时观测一致就返回 1，否则返回 0。

相关：`dt-length-hack-data`、`dt-pref-pair-code`、`dt-annotator-protocol`、`dt-judge-bias`
