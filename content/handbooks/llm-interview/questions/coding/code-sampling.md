---
id: code-sampling
section: coding
order: 12
level: S
title: 手写 Temperature + Top-p Sampling：顺序、数值稳定性和边界怎么处理？
quick: "先按 temperature 缩放 logits，再做稳定 softmax；Top-p 应按概率从高到低累积，保留最小的累计质量不少于 $p$ 的 token 集合后重新归一化并采样。要处理 $T\\to 0$、$p$ 边界、NaN/Inf 和至少保留一个 token。"
tags:
  - Coding
  - Sampling
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Generation strategies
    url: https://huggingface.co/docs/transformers/en/generation_strategies
    type: primary
---

常见误区是：先 top-p 再除 $T$，或直接 `exp(logits)` 再归一化。顺序必须是先 temperature，再 top-p：温度改 softmax 尖锐程度，nucleus 在已经温度化的分布上切。数值用减最大值的 log-softmax，并显式处理 $p=0$、全 mask。白板上比公式更容易翻的是顺序、logsumexp 减 max、以及裁空 / `NaN`；边界要能测。

## 顺序：温度整形分布，nucleus 再截尾

记原始 logits 为 $z$。Temperature 定义为 $z' = z / T$（$T\gt 0$），然后

$$
\pi_T(i)=\mathrm{softmax}(z')_i.
$$

Top-p 在 $\pi_T$ 上按概率降序排列，取最小前缀使累计质量 $\ge p$，其余置零后重新归一化，再从该 nucleus 采样。$T$ 越小分布越尖，进入 nucleus 的 token 越少；同一 $p$ 在不同温度下集合不同。所以必须先说顺序，再写代码。Top-k 若同时存在，实现必须规定与 top-p 的先后并测试；不同顺序会得到不同分布。

$T\to 0$ 时 $\pi_T$ 趋向 argmax，不要真的除以 0。$p=1$ 不截尾；$p=0$ 工程上退化成只留最大概率 token（贪心），否则累计条件会把集合裁空。若先按 $z$ 的 softmax 做 top-p 再除 $T$，截尾集合不随温度变，和常见推理实现不一致。Top-k 与 top-p 同时开时，通常先温度，再在该分布上取 k 与 p 的交集（或规定先后），写进注释和测试。重复惩罚若存在，规定是改 logits 还是改概率，以及发生在 softmax 前还是后。

## 稳定 softmax：在 log 域减最大值

`exp` 溢出的标准写法是 log-softmax：

$$
\log\pi_i = z'_i-\max_j z'_j-\mathrm{logsumexp}_k(z'_k-\max_j z'_j).
$$

全词表 mask（不允许的 token 置为 $-\infty$）时，先判断是否还存在有限 logit：一个都没有就报错或回退，不能对全 `NaN` 的 softmax 继续采样。减最大值不改变 $\mathrm{softmax}$，但让 $e^{z'-\mathrm{max}}$ 落在 $(0,1]$。手写优先 `logsumexp`：先减 max，再 `log(sum(exp(.)))`，最后 `exp(logp)`。直接 `exp(z/T)` 在大 logits 上会溢出成 `inf`，归一化变 `NaN`。Mask 与温度的次序：先把禁止位置写成 $-\infty$，再除 $T$，再减有限位置的 max。若先减 max 再 mask，可能把 max 算在即将被禁掉的 token 上，语义错了。

按「温度 → 稳定归一化 → top-p → 采样」的短实现：

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

## 边界与单测

要能测到：非法 token 全被 mask；nucleus 只剩 1 个 token 时 $q$ 是 one-hot；`p>=1` 等价于温度化的 categorical；重复惩罚 / min-p / top-k 与温度的先后固定。不同框架对「累计超过 $p$ 的边界 token 是否保留」略有出入，但至少保留一个。不要在概率上再做一次 temperature，也不要先 top-p 再除 $T$。

概率和因浮点略大于 1 时要再归一化；nucleus 权重和为 0（全 mask 或全零 bug）必须 raise；batch 维上每条样本的 nucleus 大小不同，不能假设同一个 `k`。写成断言，不要口头一句「注意数值稳定」。

白板顺序：mask 非法位置 → 温度缩放（$T\le 0$ 则贪心）→ 减有限 max 做 log-softmax → 按概率降序累计 top-p（$p\le 0$ 则贪心，且至少留一个）→ 核内重新归一化 → `choice`。All-masked 在 mask 后与归一化后两道闸。

常见错实现：在 logits 上做累计、截尾后不重新归一化就 `choice`、把被 mask 的 $-\infty$ 拿去减 max、以及 $p=0$ 时删光所有 token。单测至少覆盖：正常核、只剩一个 token、全 mask 抛错、$T=0$ 与 $p=0$ 都等于贪心、$p=1$ 等于温度化 categorical。

## 追问

- **为什么不能先 top-p 再 temperature？** Nucleus 依赖当前概率序。先截尾再改 $T$，等于在另一个分布上采样，和 Transformers 默认 generation 策略不一致。顺序必须写进代码注释和单测。
- **$p=0$ 怎么办？** 裁空会让归一化失败。实现上当作贪心，只留 $\arg\max$。不要对空集合做 `choice`。这和 $T\to 0$ 应落到同一 token。
- **all-masked 怎么办？** 不允许的集合里没有有限 logit，softmax 全是 `NaN`。应 `raise` 或回退到调用方，不要静默采样。入口检查与归一化后检查要做两次。
- **log-softmax 和 `exp` 再归一化差在哪？** 大 logits 下 `exp` 溢出成 `inf`；减 max 的 logsumexp 保持有限。这是数值题，不是风格题。Mask 后必须在有限位置上取 max，不能把 $-\infty$ 当 max。
