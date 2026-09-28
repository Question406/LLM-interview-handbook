---
id: apple-topk-sample
section: apple
order: 3
level: A
title: Apple 电面：温度、top-k、nucleus 顺序，端侧为什么常 top-k？
quick: >-
  先温度缩放 logits，再 top-k 截尾，再 nucleus；最后 softmax 采样。顺序反了截的是另一套分布。端侧常先
  top-k：候选数固定、延迟可预期，ANE 也好编静态图。不要先截断再除 $T$。
tags:
  - Apple
  - Sampling
  - Top-k
  - On-device
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: The Curious Case of Neural Text Degeneration
    url: https://arxiv.org/abs/1904.09751
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

Apple Siri / Intelligence 相关 MLE 电面常把 sampling 和 attention、k-means 放在同一批 ML coding 里，同一簇公开讨论见 `apple-mha-code`。本题不是某条带 URL 的逐字真题，按「手写解码 + 端侧约束」收。Exponent 的 Apple MLE 指南也写：on-device 岗会问延迟、量化、推理限制，采样参数正好落在这条线上。

## 顺序：温度先改分布，再裁

记 logits 为 $z\in\mathbb{R}^{|V|}$。端上词表大约 49k（Apple 公开的 on-device 模型）。

1. 温度：$z' = z / T$，$T>0$。$T<1$ 更尖，$T>1$ 更平。$T\to 0$ 不要真除零，退化成 argmax。
2. Top-k：只保留 $z'$ 里最大的 $k$ 个，其余置成 $-\infty$（或足够负的有限值，见 `apple-ondevice-quant`）。
3. Nucleus / top-p：在已经温度化、且过了 top-k 的分布上，按概率降序累加，取最小前缀使质量 $\ge p$，其余清掉，再归一化。
4. 从剩余分布采样。禁止生成的控制符在温度之前就 mask 掉。

常见错法：先 softmax 再除 $T$；或先 top-p 再除 $T$。那样截尾集合不随温度变，和常见开源实现也对不上。Top-k 与 top-p 同时开时必须规定先后：业界默认温度 → top-k → top-p。两种顺序留下的 token 不同，面试里把约定说死比争论「哪个更正确」重要。

$p=1$ 等于关掉 nucleus；$p=0$ 或 $k=1$ 应退化成贪心，不能把候选裁空再除零。全词表被 mask 时要报错或回退，不要对全 `NaN` 的 softmax 继续抽。

## 端侧为什么常 top-k

云端可以每步对十万词表做完整排序再核。手机不行。

- 延迟可预期。Top-k 是找最大 $k$ 个，堆或 `np.partition`，最坏 $O(|V|+k\log k)$，候选数固定。Nucleus 要先出全词表概率再扫前缀，保留个数随 $p$ 和当前分布变，p99 会抖。Siri 语音链路的预算见 `apple-siri-latency`，解码一步必须是微秒到亚毫秒，不能偶发卡十几毫秒。
- 静态 shape。ANE 几乎要求固定形状，见 `apple-ane`。Top-k 的候选张量永远是 $[B,k]$；nucleus 的有效长度是数据依赖的，图要为最坏 $|V|$ 付款，或退回 CPU。
- 小模型尾巴脏。On-device 大约 3B。温度一升高，长尾会冒出乱码、语言混杂。Top-k 把尾巴直接砍掉，比只调 $p$ 更稳。产品侧摘要、改写经常 $k=1$ 或很小的 $k$，要的是可复现不是多样性。
- 功耗。Apple 公开数字：iPhone 15 Pro 上大约 0.6 ms 每个 prompt token 的首 token、约 30 token/s 的生成（投机解码之前）。采样若每步全排序，会把这 30 token/s 吃掉一截，还占不到 Neural Engine。

我会主动说：创造性写作可以再叠一个较大的 $p$；工具调用、槽位、日期，贪心或很小的 $k$。不要一套超参打所有 adapter。

## 白板可以写到这个密度

```python
import numpy as np

def sample_temp_topk_topp(logits, T, k, p, rng):
    z = np.asarray(logits, np.float64)
    if T <= 0:
        return int(np.argmax(z))
    z = z / T
    if k is not None and k < z.size:
        thr = np.partition(z, -k)[-k]
        z = np.where(z >= thr, z, -np.inf)
    finite = np.isfinite(z)
    z = z - np.max(np.where(finite, z, -np.inf))
    pr = np.exp(np.where(np.isfinite(z), z, -np.inf))
    pr = np.where(np.isfinite(pr), pr, 0.0)
    s = pr.sum()
    if s <= 0:
        raise ValueError("all-masked")
    pr /= s
    if p is not None and p < 1:
        order = np.argsort(-pr)
        n = int(np.searchsorted(np.cumsum(pr[order]), p)) + 1
        keep = order[: max(n, 1)]
        q = np.zeros_like(pr)
        q[keep] = pr[keep]
        pr = q / q.sum()
    return int(rng.choice(pr.size, p=pr))
```

电面 15 分钟写完正向、说清顺序和 $T\le 0$ / 裁空，就够过。数值稳定用减 max，不要 `exp(z)` 直接炸。

## 追问

- **为什么不永远 nucleus？** 质量上 nucleus 往往更自然，但端上要为最坏 $|V|$ 和可变候选付钱。先 top-k 再较小的 $p$，是延迟和质量的折中。
- **和 KV cache 的关系？** 采样只看当前 logits，不改 cache。但错误采样会让后续 token 在脏前缀上续写，语音里很难撤回已经读出的词，所以产品超参偏保守。
- **投机解码？** Apple 公开文说 30 token/s 是投机之前的数。草稿模型也要同一套截断策略，否则验证分布对不上。
- **mask 用 $-\infty$ 在 ANE 上？** 采样若仍在 CPU 上做小 $k$ 的 softmax，fp32 的 $-\infty$ 可以。若 logits 已经量化，见 `apple-ondevice-quant`。
