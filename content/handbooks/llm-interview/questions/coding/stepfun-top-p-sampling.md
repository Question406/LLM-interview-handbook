---
id: stepfun-top-p-sampling
section: coding
order: 160
level: A
title: 阶跃星辰：手撕 top-p 采样，边界怎么处理？
quick: >-
  对 logits 做 softmax 后按概率降序累加，取刚好超过 $p$ 的最小前缀再归一化抽样。边界：$p=0/1$、全
  `-inf`、并列概率、数值下溢。拼多多日常实习二面也出过最简 top-k。
tags:
  - StepFun
  - Sampling
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 阶跃星辰大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/5cb1ebe809fd402d844cce47380a926f
    type: candidate-first-hand
---

## 真题记录

- 公司：阶跃星辰（StepFun）
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-03-27
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：手撕 **“top-p sampling、grpo”**

最常见的翻车是把 nucleus 写成「随机 argmax」：先 `softmax`，再随便抽一个高分 token，既没有累计质量，也没有截尾后重归一化。评委要看的是：在哪套分布上裁、累计刚好 $\ge p$ 的那一个是否留下、以及 $p\to 0$ / 全 mask 会不会裁空。同面若还手撕 GRPO，采样题不要和组内优势卡混成一句「随机采样」。完整温度+top-p 顺序见 `code-sampling`；本题按阶跃原帖把边界讲完即可。

## 流程：先合法化，再按概率序截核

记未归一化 logit 为 $z$。先把禁词写成 $-\infty$，再在有限位置上做稳定 softmax：

$$
\pi_i=\mathrm{softmax}(z)_i,\qquad
\mathcal{N}=\min\bigl\{k:\textstyle\sum_{j=1}^{k}\pi_{(j)}\ge p\bigr\}.
$$

其中 $\pi_{(j)}$ 是降序概率。核 $\mathcal{N}$ 内重新归一化后 `multinomial`。$p=1$ 退回全合法词表；$p\le 0$ 或实现上 $p\to 0$ 退回 $\arg\max$，并保证 $|\mathcal{N}|\ge 1$。并列概率用稳定排序（`mergesort` / 不打乱并列键），不要因为浮点抖动把本该留下的边界 token 丢掉。和 top-k 同时开时，必须先说清顺序：常见是先截 $k$ 再截 $p$，反序会得到另一套核，单测对不上。

## 边界与短实现

空词表或全体被 mask 时，softmax 全是 `NaN`，必须 `raise`，不能静默抽。bf16 / fp16 的 softmax 升到 fp32（或减 max 的 logsumexp）。累计必须在**概率序**上做，而不是 logit 序：温度或重复惩罚会改相对大小。截尾后若不重归一化就 `choice`，概率和 $\lt 1$，实现未定义。

```python
import numpy as np

def top_p_sample(logits, p, rng, mask=None):
    z = np.asarray(logits, dtype=np.float64)
    if mask is not None:
        z = np.where(mask, z, -np.inf)
    if not np.isfinite(z).any():
        raise ValueError("all-masked")
    z = np.where(np.isfinite(z), z, -np.inf)
    if p <= 0:
        return int(np.argmax(z))
    z = z - np.max(z)
    prob = np.exp(z - np.logaddexp.reduce(z))
    order = np.argsort(-prob, kind="mergesort")
    k = int(np.searchsorted(np.cumsum(prob[order]), min(p, 1.0))) + 1
    keep = order[:k]
    q = np.zeros_like(prob); q[keep] = prob[keep]; q /= q.sum()
    return int(rng.choice(q.size, p=q))
```

`searchsorted(..., side="left")+1` 保证至少 1 个 token；$p\ge 1$ 时 `min(p,1)` 不截尾。`mergesort` 让并列键可复现。同面 GRPO 手撕指到 `stepfun-grpo-group-advantage` / `stepfun-grpo-loss-handwrite`。

## 追问

- **$p=0$ 和 $p=1$ 各走哪条分支？** $p\le 0$ 贪心；$p\ge 1$ 全合法词表。都不要对空核 `choice`。
- **为什么累计不能在 logits 上做？** 核的定义是概率质量 $\ge p$，logit 序在温度或惩罚后会变，质量含义不对。
- **全 `-inf` 怎么办？** 入口与归一化后各挡一次，`raise` 而不是抽 `NaN`。
- **和 top-k 谁先？** 先说清顺序并写进测试；现场默认先 $k$ 再 $p$。采样不是随机 argmax。
