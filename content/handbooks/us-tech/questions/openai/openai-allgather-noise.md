---
id: openai-allgather-noise
section: openai
order: 2
level: S
title: OpenAI：noisy 链路上实现 all_gather，轮数 bound 怎么推？
quick: >-
  先写对 ring all_gather；有噪声时把目标改成“误差 $\varepsilon$ 内恢复 float”，只需传约 $\log_2(\mathrm{range}/\varepsilon)$ 位，再按位做重复码。
tags:
  - 完整编程练习
  - OpenAI
  - Distributed
  - Information Theory
  - all_gather
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: OpenAI Research Engineer Interview Experience (2025)
    url: https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2
    type: candidate-first-hand
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题；原帖没有给出信道模型，这里选了二元对称信道（BSC）。Python 3 + NumPy，CPU 上验证。

### 题面、接口与约束

- `noisy_ring_all_gather(values, extent, eps, flip_p, delta, rng) -> (result, stats)`：模拟同步的单向环 all_gather。`values` 形状 `[N]`，第 $i$ 个节点一开始只持有 `values[i]`。返回的 `result` 形状 `[N, N]`，第 `rank` 行是该节点按 origin 排列的全体估计；`stats` 包含量化位宽 `bits`、重复次数 `repetitions` 和总通信轮数 `rounds`。
- 每个值都在 $[0, \text{extent}]$ 内。先等间距量化，保证没有传输错误时绝对误差不超过 `eps`。
- 信道是 BSC：每次传输每个 bit 独立地以概率 $p$（`flip_p`，$0\le p<1/2$）翻转。每个 bit 重复发送奇数 $R$ 次，接收端多数表决。$R$ 的取值要保证全网所有消息中任何一个 bit 译码出错的总概率不超过 `delta`。
- 只模拟 BSC，不混用加性高斯信道。$N\le 16$，量化位宽不超过 32 位；参数非法时抛 `ValueError`。

### 输入输出示例

```text
values = [0, 0.5, 1], extent = 1, eps = 0.05, flip_p = 0
-> 每个 rank 的结果相同，每个估计误差 ≤ 0.05

values = [0.3]（N = 1）
-> 不发生通信，rounds = 0
```

### 解题思路与正确性

量化：取 $K=\lceil \text{extent}/(2\varepsilon)\rceil$ 个间隔，间隔宽度 $\text{extent}/K\le 2\varepsilon$，四舍五入到最近的格点，误差不超过 $\varepsilon$。每个值需要 $b=\lceil\log_2(K+1)\rceil$ 位。

重复码：一个 bit 发 $R$ 次，多数表决出错需要至少一半次数被翻转。由 Hoeffding 不等式，出错概率至多 $\exp(-R(1-2p)^2/2)$。每个值要沿环走 $N-1$ 跳，每跳都重新译码再转发，所以全网一共有 $N(N-1)b$ 次“一个 bit 过一跳”的事件。用 union bound，令 $N(N-1)b\cdot\exp(-R(1-2p)^2/2)\le\delta$，得到

$$
R \ge \frac{2\ln\bigl(N(N-1)b/\delta\bigr)}{(1-2p)^2},
$$

再取成奇数。

环的模拟：第 $r$ 步，rank $i$ 把 origin 为 $(i-r)\bmod N$ 的值发给 rank $i+1$。每一步先让所有节点同时发送，再统一写入，新收到的数据只能在下一步转发，避免模拟里出现零延迟的多跳。

### 完整参考实现（Python 3）

```python
import math

import numpy as np


def noisy_ring_all_gather(values, extent, eps, flip_p, delta, rng):
    """BSC 上的单向环 all_gather：量化 + 按位重复码多数表决。

    返回 (result, stats)：result[rank, origin] 是 rank 对 values[origin] 的估计；
    stats 含 bits、repetitions、rounds。
    """
    values = np.asarray(values, float)
    if values.ndim != 1 or len(values) == 0 or not np.isfinite(values).all():
        raise ValueError("values must be a non-empty 1-D array of finite numbers")
    if not math.isfinite(extent) or extent <= 0:
        raise ValueError(f"extent must be positive and finite, got {extent}")
    if (values < 0).any() or (values > extent).any():
        raise ValueError(f"values must lie in [0, {extent}]")
    if eps <= 0:
        raise ValueError(f"eps must be positive, got {eps}")
    if not 0 <= flip_p < 0.5:
        raise ValueError(f"flip_p must be in [0, 0.5), got {flip_p}")
    if not 0 < delta < 1:
        raise ValueError(f"delta must be in (0, 1), got {delta}")

    n = len(values)
    levels = max(1, math.ceil(extent / (2 * eps)))  # 间隔 extent/levels <= 2 * eps
    bits = max(1, math.ceil(math.log2(levels + 1)))
    if bits > 32:
        raise ValueError(f"needs {bits} bits, but this practice allows at most 32")
    quantized = np.floor(values / extent * levels + 0.5).astype(np.int64)

    # union bound：全网 n(n-1)*bits 次 bit-hop，每次出错概率 <= exp(-R(1-2p)^2/2)
    total_bit_hops = max(1, n * (n - 1) * bits)
    repetitions = math.ceil(2 * math.log(total_bit_hops / delta) / (1 - 2 * flip_p) ** 2)
    if repetitions % 2 == 0:
        repetitions += 1  # 奇数次，多数表决不会平票

    seen = [{rank: int(q)} for rank, q in enumerate(quantized)]  # rank -> {origin: 量化值}
    for step in range(n - 1):
        received = []
        for rank in range(n):
            origin = (rank - step) % n  # 第 step 步，rank 转发 origin 为 rank-step 的值
            integer = seen[rank][origin]
            packet = np.array([(integer >> b) & 1 for b in range(bits)], dtype=np.int64)
            flips = rng.random((repetitions, bits)) < flip_p
            decoded = np.logical_xor(packet, flips).sum(axis=0) > repetitions // 2
            number = sum(int(bit) << b for b, bit in enumerate(decoded))
            received.append(((rank + 1) % n, origin, number))
        for rank, origin, number in received:  # 同步：本步收到的数据下一步才转发
            seen[rank][origin] = number

    result = np.array([
        [min(levels, max(0, row[origin])) * extent / levels for origin in range(n)]
        for row in seen
    ])
    stats = {"bits": bits, "repetitions": repetitions, "rounds": (n - 1) * repetitions}
    return result, stats
```

### 可执行测试

```python
def expect_value_error(*args):
    try:
        noisy_ring_all_gather(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError for {args[:5]}")


values = np.array([0.0, 0.23, 0.91, 1.0])

# 无噪声：误差不超过 eps，每个 rank 结果相同
out, stats = noisy_ring_all_gather(values, 1, 0.02, 0, 0.01, np.random.default_rng(1))
assert np.max(np.abs(out - values)) <= 0.02 + 1e-12
assert np.allclose(out, out[0])

# 轮数 = (N - 1) * R，R 为奇数
assert stats["rounds"] == 3 * stats["repetitions"]
assert stats["repetitions"] % 2 == 1

# 有噪声：按 delta 选的 R 足够让这次结果仍在误差内
out, _ = noisy_ring_all_gather(values, 1, 0.02, 0.1, 0.001, np.random.default_rng(7))
assert np.max(np.abs(out - values)) <= 0.02 + 1e-12

# N = 1 不通信
_, stats = noisy_ring_all_gather([0.3], 1, 0.01, 0.1, 0.01, np.random.default_rng(2))
assert stats["rounds"] == 0

# 噪声越大，需要的重复次数越多
_, low = noisy_ring_all_gather(values, 1, 0.02, 0.05, 0.01, np.random.default_rng(3))
_, high = noisy_ring_all_gather(values, 1, 0.02, 0.3, 0.01, np.random.default_rng(3))
assert high["repetitions"] > low["repetitions"]

# 非法参数
rng = np.random.default_rng(0)
expect_value_error([1.5], 1, 0.1, 0.1, 0.01, rng)
expect_value_error([0.5], 1, 0.1, 0.5, 0.01, rng)
expect_value_error([0.5], 1, 0.0, 0.1, 0.01, rng)
expect_value_error([], 1, 0.1, 0.1, 0.01, rng)
```

### 复杂度与追问

设节点数为 $N$，量化位宽为 $b$，重复次数为 $R$。同步轮数是 $(N-1)R$，总共传输 $N(N-1)bR$ 个 bit；模拟需要 $O(N^2 + Rb)$ 的空间。

- 追问「这就是答案吗」：这是在 BSC 和重复码这两个明确假设下可以证明的上界，不是原帖未知信道条件下的唯一答案。重复码远非最优，换成真正的纠错码（例如线性分组码）可以用接近信道容量的码率传输，轮数会少很多。

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer
- 轮次：Coding + ML stats（候选人称这是整个 loop 最难的一轮）
- 来源：Exponent 2025 报告
- 题面大意：实现多节点 all_gather；通信有噪声时，推导达到目标精度需要多少轮；再改进，因为 naive 的上界太慢。关键观察是传的是 float，不是任意实数。

这道题容易答成“再 all_gather 一次就行”，或者直接背集合通信复杂度 $2(N-1)M/N$。OpenAI 只是把集合通信当载体，真正考的是在噪声信道上要传多少信息。提示很少，需要自己把问题归结成信息论问题。

## 第一部分：先写对无噪声 all_gather

$N$ 张卡，每张卡有一块大小为 $M/N$ 的数据，最后每张卡都要拿到完整的 $M$。Ring all_gather 要走 $N-1$ 步，每一步每张卡发出一块、收到一块，带宽项约为 $(N-1)/N \cdot M$。$N$ 为 2 的幂时，recursive doubling 的延迟更好。白板上要写出 send/recv 的顺序和最终每张卡的内存布局，不要只报 NCCL 原语名。

和 all_reduce 的区别要主动讲：all_reduce 是把各卡数据归约成一份，再广播（或 reduce-scatter 后再 all_gather）；all_gather 只是拼接。训练里 Tensor Parallel 的列并行、MoE 的 token 分发，都更接近 gather 而不是 reduce。

## 噪声模型与轮数必须分开约定

上面的练习明确采用独立 bit 翻转的 BSC 信道（$0\le p<1/2$），只证明重复码加多数表决的保守上界，推导见练习的「解题思路与正确性」。这个上界不是最优纠错码的复杂度。

浮点数只有有限的表示位数，但要不要容许量化误差，取决于题目是否要求 bit-exact。允许绝对误差时，还要明确值域；不能仅凭 IEEE float 精度有限，就擅自把无损传输改成有损。练习里的均匀量化只适用于已经声明的有界区间，此时每个值的有效信息量约为 $\log_2(\mathrm{range}/\varepsilon)$ 位。

加性高斯噪声下多次观测取平均是另一类问题，所需轮数取决于噪声方差、目标精度和成功概率。谈信道容量还需要功率、带宽等约束，不能和 BSC 的翻转概率混进同一个公式。原面经没有完整披露这些条件，这里不为它编造唯一的轮数答案。
