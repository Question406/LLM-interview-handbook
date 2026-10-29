---
id: code-sampling
section: coding
order: 12
level: S
title: 手写 Temperature + Top-p Sampling：顺序、numerical stability 和 edge cases 怎么处理？
quick: >-
  先按 temperature 缩放 logits，再做减 max 的稳定 softmax；Top-p
  在这个温度化的分布上按概率从高到低累积，保留累计质量不少于 $p$ 的最小集合，renormalization 后 sampling。edge-case
  handling 需要覆盖 $T\to 0$、$p$ 的两端、NaN/Inf，并且至少保留一个 token。
tags:
  - Coding
  - Sampling
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Generation strategies
    url: 'https://huggingface.co/docs/transformers/en/generation_strategies'
    type: primary
---

## 题目描述

给定一维 vocabulary logits，返回一次 sampling 得到的 token 下标。sampling 需要同时支持温度、top-p 概率截断和合法 token mask，并能够由调用者提供随机数生成器以复现结果。

### 接口与约定

`sample_temp_top_p(logits,T,p,rng,mask=None)`：logits 长度为 V；mask 若给出，长度同为 V，True 表示允许 sampling。保证至少有一个合法且分数有限的 token。返回 0 到 V-1 的一个整数下标。

T<=0 或 p<=0 时，从合法 token 中返回最高 logits 的下标，最高值平票时采用 NumPy argmax 的第一个下标。否则在合法 token 上按温度 T 形成概率，按概率降序保留累计质量第一次达到 p 的最短前缀，再在保留集合上 renormalization sampling；p>=1 表示不因累计质量排除任何正常概率项。默认测试避开截断处的概率平票。

### 示例

```text
logits=[0,5], T=0, p=1 -> 必定返回1
logits=[9,0], T=1, p=1, mask=[False,True] -> 必定返回1
logits=[0,5], T=1, p=0.01 -> 必定返回1
```

随机分支不要求每次都得到同一个 token，但同一生成器状态与同一输入应产生可复现的 sampling 序列。以上细节为手册统一练习约定。

## 解题思路与参考答案

顺序是先 temperature、再 top-p：先把 logits 除以 $T$，用减最大值的 log-softmax 得到概率，再在这个分布上按概率从高到低累积，切出 nucleus，renormalization 后 sampling。温度决定分布有多尖，nucleus 是在已经温度化的分布上切的。比如把温度调低，原来要好几个 token 才凑够 $p$，现在可能头一个就够了。白板上比公式更容易翻车的是三件事：顺序，logsumexp 里减 max，还有被裁空或者出现 `NaN` 的 edge cases，这些都要能测出来。

常见的错是先做 top-p 再除 $T$，或者直接 `exp(logits)` 再 normalization。前一种截尾集合不随温度变，和常见推理实现不一致；后一种在大 logits 上会溢出。

## 先温度，再 top-p

记原始 logits 为 $z$。Temperature 定义为 $z' = z / T$（$T\gt 0$），然后

$$
\pi_T(i)=\mathrm{softmax}(z')_i.
$$

Top-p 在 $\pi_T$ 上按概率降序排列，取累计质量 $\ge p$ 的最小前缀，其余置零，renormalization，再从这个 nucleus 里 sampling。$T$ 越小分布越尖，进入 nucleus 的 token 越少，所以同一个 $p$ 在不同温度下切出来的集合不一样。这就是为什么写代码之前要先把顺序说清楚。

几个端点要单独处理。$T\to 0$ 时 $\pi_T$ 趋向 argmax，别真的除以 0。$p=1$ 就是不截尾；$p=0$ 在工程上退化成只留概率最大的 token，也就是贪心，否则累计条件会把集合裁空。

如果同时开了 top-k，实现里要规定它和 top-p 谁先谁后，并写测试，顺序不同得到的分布也不同。通常是先温度，再在这个分布上取 k 和 p 的交集，或者明确规定先后，写进注释和测试。有重复惩罚的话，也要规定它改的是 logits 还是概率，发生在 softmax 之前还是之后。

## 数值稳定：在 log 域减最大值

防 `exp` 溢出的标准写法是 log-softmax：

$$
\log\pi_i = z'_i-\max_j z'_j-\mathrm{logsumexp}_k(z'_k-\max_j z'_j).
$$

减最大值不改变 $\mathrm{softmax}$，但能让 $e^{z'-\mathrm{max}}$ 落在 $(0,1]$。手写时优先用 `logsumexp`：先减 max，再 `log(sum(exp(.)))`，最后 `exp(logp)`。直接算 `exp(z/T)` 的话，大 logits 会溢出成 `inf`，normalization 之后就是 `NaN`。

mask 也要放进这个顺序里。全 vocabulary mask 是指把不允许的 token 置为 $-\infty$，之后先检查还有没有有限的 logit，一个都没有就报错或回退，不能对全是 `NaN` 的 softmax 继续 sampling。顺序是先把禁止位置写成 $-\infty$，再除 $T$，再在有限位置上减 max。如果先减 max 再 mask，max 可能恰好算在一个马上要被禁掉的 token 上，语义就错了。

按「温度 → 稳定 normalization → top-p → sampling」写出来是这样：

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

`p<=0` 和 `T<=0` 都走 argmax。`searchsorted(..., side="left")+1` 保证 nucleus 里至少有一个 token，$p$ 再小也是。全 mask 在入口和 normalization 之后各挡一次，免得 `NaN` 进到 `choice` 里。

累计用的是温度化之后的概率顺序，不是 logit 顺序。温度会改变相对大小，但它是单调变换，argmax 不变，所以 $T\to 0$ 和 $p=0$ 都应该落到同一个贪心 token 上（在有限集合里）。$p$ 略大于 0 时，要保留累计刚好超过 $p$ 的那个 cutoff token，这是 nucleus 的标准定义；在累计严格大于 $p$ 时把最大的 token 也删掉，就写错了。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

先测 T=0 的贪心分支和仅允许一个 token 的 mask，预期都是确定的。正温度分支用很小的 p 只保留概率最大的 token，并固定生成器种子。

```python
rng = np.random.default_rng(7)
assert sample_temp_top_p([0.0, 5.0], 0, 1.0, rng) == 1
assert sample_temp_top_p([9.0, 0.0], 1.0, 1.0, rng, mask=[False, True]) == 1
assert sample_temp_top_p([0.0, 5.0], 1.0, 0.01, rng) == 1
try:
    sample_temp_top_p([0.0, 1.0], 1.0, 1.0, rng, mask=[False, False])
except ValueError:
    pass
else:
    raise AssertionError("all-masked input must fail")
print("simple tests passed")
```

## Edge Cases 与 Unit Tests

白板上的完整顺序是：mask 非法位置 → 温度缩放（$T\le 0$ 则贪心）→ 在有限位置上减 max 做 log-softmax → 按概率降序累计 top-p（$p\le 0$ 则贪心，且至少留一个）→ 在核内 renormalization → `choice`。all-masked 在 mask 之后和 normalization 之后各有一道闸。

单测至少覆盖这几种：正常的核；nucleus 只剩 1 个 token 时 $q$ 是 one-hot；非法 token 全被 mask 时抛错；$T=0$ 和 $p=0$ 都等于贪心；`p>=1` 等价于温度化的 categorical。重复惩罚、min-p、top-k 和温度的先后要固定下来。不同框架对「累计超过 $p$ 的那个 cutoff token 留不留」略有出入，但至少都会保留一个。也别在概率上再做一次 temperature。

常见的错实现还有几种：在 logits 上做累计；截尾之后没 renormalization 就 `choice`；把被 mask 的 $-\infty$ 拿去减 max；$p=0$ 时把 token 删光。概率和因为浮点误差略大于 1 时要再 normalization；nucleus 的权重和为 0（全 mask 或者全零 bug）必须 raise；batch 里每条样本的 nucleus 大小不同，不能假设大家共用一个 `k`。这些都写成断言，别只在口头上说一句「注意数值稳定」。

## 追问

**为什么不能先 top-p 再 temperature？**
Nucleus 依赖当前的概率顺序。先截尾再改 $T$，等于在另一个分布 upsampling，和 Transformers 默认的 generation 策略不一致。所以顺序要写进代码注释和单测。

**$p=0$ 怎么办？**
当作贪心，只留 $\arg\max$。按累计条件走会把集合裁空，normalization 就失败了，也别对空集合做 `choice`。它应该和 $T\to 0$ 落到同一个 token。

**all-masked 怎么办？**
`raise` 或者交回调用方处理，别静默 sampling。允许的集合里没有有限 logit 时，softmax 全是 `NaN`。入口和 normalization 之后要各检查一次。

**log-softmax 和直接 `exp` 再 normalization 差在哪？**
差在数值上。大 logits 下 `exp` 会溢出成 `inf`，减 max 的 logsumexp 能保持有限，这和代码风格无关。mask 之后必须在有限位置上取 max，不能把 $-\infty$ 当成 max。
