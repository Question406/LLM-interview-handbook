---
id: code-sampling
section: coding
order: 12
level: S
title: 手写 Temperature + Top-p Sampling：顺序、数值稳定性和边界怎么处理？
quick: >-
  先按 temperature 缩放 logits，再做稳定 softmax；Top-p 应按概率从高到低累积，保留最小的累计质量不少于 $p$ 的 token
  集合后重新归一化并采样。要处理 $T\to 0$、$p$ 边界、NaN/Inf 和至少保留一个 token。
tags:
  - Coding
  - Sampling
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Generation strategies
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: primary
---

这题考的不只是会调 API，而是能说清「在什么分布上裁剪」。顺序必须是 **先 temperature，再 top-p**：温度改的是 softmax 的尖锐程度，nucleus 是在这个已经温度化的分布上切。先 top-p 再除 $T$，等于在另一套概率上裁，和常见推理实现不一致。数值上不要直接 `exp(logits)`，要用减最大值的 log-softmax，并显式处理 $p=0$、全 mask。评委要看三件事：顺序有没有写对、logsumexp 有没有减 max、以及 $p=0$ 与全部非法 token 会不会把集合裁空或产出 `NaN`。这三件事比背公式更常在白板上翻车。采样函数必须在这些边界上可测试，而不是只在正常 logits 上能跑通。

## 顺序：温度整形分布，nucleus 再截尾

记原始 logits 为 $z$。Temperature 定义为 $z' = z / T$（$T\gt 0$），然后

$$
\pi_T(i)=\mathrm{softmax}(z')_i.
$$

Top-p 在 $\pi_T$ 上按概率降序排列，取最小前缀使累计质量 $\ge p$，其余置零后重新归一化，再从该 nucleus 采样。$T$ 越小分布越尖，进入 nucleus 的 token 越少；同一 $p$ 在不同温度下集合不同。所以面试必须先说顺序，再写代码。Top-k 若同时存在，实现必须规定与 top-p 的先后并测试；不同顺序会得到不同分布。

$T\to 0$ 时 $\pi_T$ 趋向 argmax，不要真的去除以 0。$p=1$ 表示不截尾；$p=0$ 在工程上应退化成只保留最大概率的那个 token（贪心），否则累计条件会把集合裁空。面试要主动说「nucleus 定义在温度化之后的分布上」。若先按 $z$ 的 softmax 做 top-p，再除 $T$，等于截尾集合不随温度变，和开源推理栈常见实现不一致，单测也会对不上。Top-k 与 top-p 同时开时，通常先温度，再在该分布上取 k 与 p 的交集（或规定先后），必须写进注释和测试，因为两种顺序保留的 token 不同。重复惩罚若存在，也应规定是改 logits 还是改概率，并且发生在 softmax 之前还是之后。

## 稳定 softmax：在 log 域减最大值

`exp` 溢出的标准写法是 log-softmax：

$$
\log\pi_i = z'_i-\max_j z'_j-\mathrm{logsumexp}_k(z'_k-\max_j z'_j).
$$

全词表 mask（不允许的 token 置为 $-\infty$）时，必须先判断是否还存在有限 logit：一个都没有就应报错或回退，不能对全 `NaN` 的 softmax 继续采样。减最大值不会改变 $\mathrm{softmax}$，但让 $e^{z'-\mathrm{max}}$ 落在 $(0,1]$。不要用概率域反复除温度。现场若被要求手写，优先写 `logsumexp`：先减 max，再 `log(sum(exp(.)))`，最后 `exp(logp)` 得到概率。直接 `exp(z/T)` 在 logits 为几十、几百时会溢出成 `inf`，归一化变成 `NaN`。Mask 与温度的次序：先把禁止位置写成 $-\infty$，再除 $T$（$-\infty/T$ 仍是 $-\infty$），再减有限位置的 max。若先减 max 再 mask，可能把 max 算在即将被禁掉的 token 上，稳定性仍在，但语义错了。

下面是一段按「温度 → 稳定归一化 → top-p → 采样」的短实现，边界写在函数里：

```python
import numpy as np

def sample_temp_top_p(logits, T, p, rng, mask=None):
    z = np.asarray(logits, dtype=np.float64)
    if mask is not None:
        z = np.where(mask, z, -np.inf)
    if not np.isfinite(z).any():
        raise ValueError("all-masked")
    if T <= 0 or p <= 0:
        z = np.where(np.isfinite(z), z, -np.inf)
        return int(np.argmax(z))
    z = z / T
    z = z - np.max(np.where(np.isfinite(z), z, -np.inf))
    z_safe = np.where(np.isfinite(z), z, -np.inf)
    logp = z_safe - np.logaddexp.reduce(z_safe)
    prob = np.exp(logp)
    prob = np.where(np.isfinite(prob), prob, 0.0)
    s = prob.sum()
    if s <= 0:
        raise ValueError("all-masked")
    prob /= s
    order = np.argsort(-prob)
    cdf = np.cumsum(prob[order])
    k = int(np.searchsorted(cdf, min(p, 1.0), side="left")) + 1
    keep = order[:k]
    q = np.zeros_like(prob)
    q[keep] = prob[keep]
    q /= q.sum()
    return int(rng.choice(q.size, p=q))
```

`p<=0` 与 `T<=0` 走 argmax；`searchsorted(..., side="left")+1` 保证 nucleus 至少一个 token（即使 $p$ 极小）。全 mask 在入口和归一化后各挡一次，避免 `NaN` 进入 `choice`。累计用的是温度化后的概率序，不是 logit 序：温度会改变相对大小，但单调变换下 argmax 不变，所以 $T\to 0$ 与 $p=0$ 都应落到同一个贪心 token（在有限集合上）。`p` 略大于 0 时保留累计刚超过 $p$ 的那个边界 token，这是 nucleus 的标准定义，不要在累计严格大于 $p$ 时把最大 token 也删掉。

## 还要测的边界，而不只是 happy path

白板之外应能说出测试点：非法 token 全被 mask；nucleus 只剩 1 个 token 时 $q$ 是 one-hot；`p>=1` 等价于温度化的 categorical；重复惩罚 / min-p / top-k 与温度的先后必须固定并写进单测。不同框架对「累计超过 $p$ 的那一个 token 是否保留」约定略有出入，但 **至少保留一个** 是硬约束。不要在概率上再做一次 temperature，也不要先 top-p 再除 $T$。评委常追问的边界还有：概率和因浮点误差略大于 1 时要不要再归一化（要）；nucleus 权重和为 0（只可能来自全 mask 或全零 bug）必须 raise；batch 维上每条样本的 nucleus 大小不同，不能假设同一个 `k`。把这些写成断言，比口头说「注意数值稳定」更像写过推理代码。

白板顺序背板：mask 非法位置 → 温度缩放（$T\le 0$ 则贪心）→ 减有限 max 做 log-softmax → 按概率降序累计 top-p（$p\le 0$ 则贪心，且至少留一个）→ 核内重新归一化 → `choice`。All-masked 在 mask 后与归一化后两道闸。这和「调 API 的 temperature/top_p」不是同一道题。实现上必须先温度后 top-p：温度改的是 softmax 的尖锐程度，nucleus 在这个已经温度化的分布上按概率从高到低累计，保留最小的使质量达到 $p$ 的集合，再重新归一化采样。数值用减最大值的 log-softmax，避免 `exp` 溢出。$p=0$ 或 $T\le 0$ 走贪心；$p=1$ 不截尾；全部 mask 时没有有限 logit，必须报错而不能对 `NaN` 采样。至少保留一个 token 是硬约束。顺序、稳定性和这三条边界写对，这题才算完成。常见错实现包括：在 logits 上而不是概率上做累计（质量含义不对）、截尾后不重新归一化就 `choice`（概率和小于 1）、把被 mask 的 $-\infty$ 拿去减 max（max 变成 $-\infty$，全体变 `NaN`）、以及 $p=0$ 时让累计条件删光所有 token。单测至少覆盖：正常核、只剩一个 token、全 mask 抛错、$T=0$ 与 $p=0$ 都等于贪心、$p=1$ 等于温度化 categorical。能把这些边界讲完，才像手写过采样，而不是调过 HuggingFace 参数。

## 追问

- **为什么不能先 top-p 再 temperature？** Nucleus 依赖当前概率序。先截尾再改 $T$，等于在另一个分布上采样，和 Transformers 默认 generation 策略不一致。顺序必须写进代码注释和单测。温度先整形，nucleus 再在该分布上截尾，这是这题的第一句话。
- **$p=0$ 怎么办？** 裁空会让归一化失败。实现上当作贪心，只留 $\arg\max$。不要对空集合做 `choice`。这和 $T\to 0$ 应落到同一 token。
- **all-masked 怎么办？** 不允许的集合里没有有限 logit，softmax 全是 `NaN`。应 `raise` 或回退到调用方，不要静默采样。入口检查与归一化后检查要做两次，防止全非法词表把采样变成未定义行为。
- **log-softmax 和 `exp` 再归一化差在哪？** 大 logits 下 `exp` 溢出成 `inf`；减 max 的 logsumexp 保持有限。这是数值题，不是风格题。Mask 后必须在有限位置上取 max，不能把 $-\infty$ 当 max。先温度后 top-p，再处理 $p=0$ 与全 mask，这三件事写进函数才算手写完成。顺序、减 max、边界缺一都会在白板上被追问到过不去。这三件事比背 API 参数更常考。顺序错了，后面的核和边界都在错误分布上。先温度、再 top-p，这句必须先说。核定义在温度化之后的分布上。截尾集合必须随温度一起变。
