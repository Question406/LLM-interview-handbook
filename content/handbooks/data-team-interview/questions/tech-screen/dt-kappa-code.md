---
id: dt-kappa-code
section: tech-screen
order: 15
level: A
title: CoderPad：两个人标同一批，Cohen's $\kappa$ 怎么算，低了改什么？
quick: >-
  我会先算 $\kappa=(p_o-p_e)/(1-p_e)$，$p_o$ 是一致率，$p_e$ 是按边际算的偶然一致。只报 90% 一致不够，类别不平衡时 $p_e$ 已经很高。
  $\kappa$ 低先改协议和例子，不要先加人。
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

我会先写混淆矩阵再算 $\kappa=(p_o-p_e)/(1-p_e)$。只报 90% 一致不够，类别不平衡时 $p_e$ 已经很高。$\kappa$ 低先改协议和例子，不要先加人。`dt-annotator-protocol` 讲协议；这里给你两列标签，别只算 `mean(a==b)`。

Cohen 1960：两名标注员、类别集合 $C$。$n_{ij}$ 是 A 标 $i$、B 标 $j$ 的条数。$p_o=\sum_i n_{ii}/N$。$p_e=\sum_i p_{i\cdot}p_{\cdot i}$，边际来自这张表。

## 先算表，再算 $\kappa$

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

先打印混淆矩阵，查看分歧集中在哪些类别。$\kappa=0.4$ 但错误全在「部分有用 / 有用」两档，如果这两档的业务含义允许合并，可以修改协议后重新标注。错误散在「拒绝 / 遵从」上，是安全题，不能合并。

## 数字怎么解释

$p_o=0.9$、正例占 95% 时，$p_e$ 已经约 0.9，$\kappa$ 接近 0。这就是「一致率好看、标签没信息」。偏好对的 chosen/rejected 若 80% 的人总是选更长的那条，一致率和长度 hack 是同一件事，见 `dt-length-hack-data`。

多人用 pairwise $\kappa$ 的中位数，或 Fleiss。现场两人版够。空标签、跳过不当成一个类，除非协议明确「无法判断」是合法类。

Llama 3 公开写了偏好要丢掉「差不多」的对。$\kappa$ 低的那一档，往往说明两个回答太难区分，直接用于 DPO 会增加噪声，见 `dt-pref-pair-code`。

## 追问

- **$\kappa$ 多少能训？** 没有通用线。安全拒答应很高；开放式有用性 0.4 到 0.6 常见，靠金标审核补。报 $\kappa$ 同时报混淆矩阵。
- **低了加人投票？** 三人多数票会把模糊题变成假金标。先修订标注说明，用 20 个争议例子解释标准，再重新标注。
- **和模型 judge 比对？** 人-人 $\kappa$ 是协议上限。人-模型更低，说明 judge 不能替代这一批，见 `dt-judge-bias`。
