---
id: kv-prefix-transformer
section: systems
order: 31
level: S
title: KV Prefix ①：多层 Transformer 的 prefill、decode 与前缀分叉
quick: >-
  每层复用自己的 K/V，只计算新后缀，RoPE 和因果 mask 从已有 cache 的绝对位置继续。用整段重算、逐 token decode、分块
  prefill 和前缀分叉对照 logits，检查缓存正确且不被分支改写。
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Attention Is All You Need
    url: 'https://arxiv.org/abs/1706.03762'
    type: primary
---

## 题目描述

实现一个小型、确定性的多层 decoder-only Transformer 前向过程，验证相同前缀的 KV 缓存能用于后缀续算和独立分支。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- 完成给定模型 `TinyTransformer(seed=0,layers=2,vocab=19,width=8,heads=2,kv_heads=1)` 的 `forward(token_ids,cache=None)` 及 `slice_cache(cache,length)`。构造器提供固定 NumPy float64 权重和配置；本题不训练、不修改权重。width % heads = 0，heads % `kv_heads` = 0，d=width/heads 为偶数。
- `token_ids` 是非空 [T] 整数序列，取值 [0,vocab)。cache 是每层一个 (K,V) 的 tuple，各张量为 [`kv_heads`,S,d]，各层 S 相同；None 表示 S=0。返回 ([T,vocab] logits, 新 cache)，新 cache 长度为 S+T，旧 cache 必须保持不变。
- 模型定义：token embedding 后，各层采用 pre-RMSNorm，`RMSNorm(x)=x/sqrt(mean(x²)+1e-6)`；attention 残差为 `x + Attention(RMSNorm(x)) @ W_o`；接着 gating MLP 残差为 `x + (SiLU(z @ W_gate) * (z @ W_up)) @ W_down`，z 是第二次 RMSNorm，SiLU(a)=a/(1+exp(-a))。最终 logits 为 RMSNorm(x) @ `W_output`。
- Q/K/V 使用各层给定的 q/k/v 权重；每个 query head 对应连续分组的一个 KV head，分数为 QKᵀ/sqrt(d)，softmax 只含绝对位置 `key_pos`<=`query_pos` 的 key。无 bias、dropout 或其他 normalization 参数。
- Q/K 使用相邻偶/奇坐标的 RoPE，角度 theta[p,j]=p*10000**(-2*j/d)，旋转为 (a*cos-b*sin,a*sin+b*cos)。新 token 绝对位置从 S 起，旧 K 已旋转；V 不旋转。每层只缓存自身的紧凑 K/V。
- `slice_cache(cache,length)` 返回每层前 length 个位置的独立副本，0<=length<=S。`computed_tokens` 每次 forward 增加 T，fingerprint 及权重不变。同一前缀 cache 可用于多个独立后缀，分支不得互相污染。

### 输入输出示例

```text
默认模型、token_ids=[1,4,2,7,3,8]：
一次 forward 返回 logits 形状 [6,19]，每层 K/V 形状 [1,6,4]。
先 forward([1,4,2])，再用其 cache forward([7,3,8])：
第二次输出等于完整输出的后3行，每层新 cache 形状 [1,6,4]。
slice_cache(第一次cache,2) -> 每层 K/V 形状 [1,2,4] 的独立副本。
TinyTransformer(seed=0,layers=1,vocab=2,width=2,heads=1,kv_heads=1)
forward([1]) 的 logits 约为 [[-0.20505793,0.06097503]]。
```

## 解题思路与参考答案

我会在每层恢复对应的 K/V，只让新后缀经过前向计算，并从已有 cache 的长度继续计算位置。整段重算、逐 token decode 和分块 prefill 应有一致 logits，两个后缀共享前缀时也不能互相改坏缓存。

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，代码为手册独立实现。接口、简化条件和测试由手册定义。依赖 Python 3与 NumPy，使用 CPU 测试数值及状态语义，不报告 GPU throughput。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `TinyTransformer.forward(token_ids,cache=None)` 和 `slice_cache`。这是确定性、单请求的 NumPy float64 多层 decoder-only 模型：token embedding、pre-RMSNorm、RoPE、GQA、attention 输出投影、残差、gating MLP、最终 normalization 与 vocabulary logits，禁用 dropout。输入非空合法整数 token，默认 vocabulary19、层数2、宽8、query heads2、KV heads1；维度关系合法。每层 cache 为 K/V 各 `[Hkv,S,d]`，全部层长度必须相同。返回新 token 的 `[T,V]` logits 和覆盖旧前缀及新后缀的每层 cache。模型权重冻结后不得改变；原 cache 不得被修改。

### 输入输出示例

输入 `[1,4,2,7,3,8]`：一次 forward 得到6行 logits；先算前3项，再用 cache 只算后3项，后缀 logits 必须等于完整计算的第3至5行。两个不同后缀从同一前缀分叉，不得互相污染。

### 解题思路与正确性

比如先算六个 token 的前三项，再把 cache 交给后三项，后缀 logits 应等于完整计算对应的三行。每层要取自己的 K/V；新 Q/K 的 RoPE 从 cache 长度开始，旧 K 已经旋转过，不能再旋转一次。矩形因果 mask 按 `key_pos <= old_len + query_offset` 判断可见性。同一模型、位置和 attention 语义保持一致，逐层就能推出后缀隐藏状态与完整前向相同。

### 完整参考实现（Python 3）

```python
import hashlib
import numpy as np


class TinyTransformer:
    """Two-or-more-layer CPU reference: RMSNorm, RoPE, GQA and gated MLP."""

    def __init__(self, seed=0, layers=2, vocab=19, width=8, heads=2, kv_heads=1):
        if layers < 1 or width % heads or heads % kv_heads or (width // heads) % 2:
            raise ValueError('head geometry')
        self.layers, self.heads, self.kv_heads = layers, heads, kv_heads
        self.width, self.d = width, width // heads
        rng = np.random.default_rng(seed)

        def weight(a, b):
            return rng.normal(scale=0.2, size=(a, b))

        self.embed = weight(vocab, width)
        self.output = weight(width, vocab)
        self.weights = []
        for _ in range(layers):
            self.weights.append(
                dict(
                    q=weight(width, width),
                    k=weight(width, kv_heads * self.d),
                    v=weight(width, kv_heads * self.d),
                    o=weight(width, width),
                    gate=weight(width, 2 * width),
                    up=weight(width, 2 * width),
                    down=weight(2 * width, width),
                )
            )
        # Frozen weights/config define the cache namespace in this exercise.
        arrays = [self.embed, self.output]
        arrays += [w[k] for w in self.weights for k in sorted(w)]
        digest = hashlib.sha256(str((layers, width, heads, kv_heads)).encode())
        for a in arrays:
            a.flags.writeable = False
            digest.update(a.tobytes())
        self.fingerprint = digest.hexdigest()
        self.computed_tokens = 0

    @staticmethod
    def norm(x):
        return x / np.sqrt(np.mean(x * x, axis=-1, keepdims=True) + 1e-6)

    @staticmethod
    def rotate(x, start):
        d = x.shape[-1]
        angle = np.arange(start, start + x.shape[1])[:, None] * 10000.0 ** (
            -np.arange(0, d, 2) / d
        )
        even, odd = x[..., 0::2], x[..., 1::2]
        out = np.empty_like(x)
        out[..., 0::2] = even * np.cos(angle) - odd * np.sin(angle)
        out[..., 1::2] = even * np.sin(angle) + odd * np.cos(angle)
        return out

    def forward(self, token_ids, cache=None):
        ids = np.asarray(token_ids)
        if ids.ndim != 1 or ids.dtype.kind not in 'iu' or not len(ids):
            raise ValueError('nonempty integer token sequence required')
        if (ids < 0).any() or (ids >= len(self.embed)).any():
            raise ValueError('token range')
        old = 0
        if cache is not None:
            if len(cache) != self.layers:
                raise ValueError('one KV pair per layer required')
            lengths = set()
            for k, v in cache:
                if (
                    k.ndim != 3
                    or k.shape != v.shape
                    or k.shape[0] != self.kv_heads
                    or k.shape[-1] != self.d
                ):
                    raise ValueError('cache shape')
                lengths.add(k.shape[1])
            if len(lengths) != 1:
                raise ValueError('layer cache lengths disagree')
            old = lengths.pop()
        x = self.embed[ids].copy()
        new_cache = []
        t = len(ids)
        for layer, w in enumerate(self.weights):
            z = self.norm(x)
            q = self.rotate(
                (z @ w['q']).reshape(t, self.heads, self.d).transpose(1, 0, 2), old
            )
            k = self.rotate(
                (z @ w['k']).reshape(t, self.kv_heads, self.d).transpose(1, 0, 2), old
            )
            v = (z @ w['v']).reshape(t, self.kv_heads, self.d).transpose(1, 0, 2)
            if cache is not None:
                k = np.concatenate((cache[layer][0], k), axis=1)
                v = np.concatenate((cache[layer][1], v), axis=1)
            new_cache.append((k, v))
            kr, vr = (np.repeat(a, self.heads // self.kv_heads, axis=0) for a in (k, v))
            scores = (q @ kr.swapaxes(-1, -2)) / np.sqrt(self.d)
            allowed = np.arange(old + t)[None, :] <= (old + np.arange(t))[:, None]
            scores = np.where(allowed[None], scores, -np.inf)
            p = np.exp(scores - scores.max(axis=-1, keepdims=True))
            p /= p.sum(axis=-1, keepdims=True)
            attended = (p @ vr).transpose(1, 0, 2).reshape(t, self.width)
            x += attended @ w['o']
            z = self.norm(x)
            gate = z @ w['gate']
            # Stable sigmoid, used only in the SiLU gate.
            e = np.exp(-np.abs(gate))
            sigmoid = np.where(gate < 0, e / (1 + e), 1 / (1 + e))
            x += (gate * sigmoid * (z @ w['up'])) @ w['down']
        self.computed_tokens += t
        return self.norm(x) @ self.output, tuple(new_cache)


def slice_cache(cache, length):
    if length < 0 or any(length > k.shape[1] for k, _ in cache):
        raise ValueError('cache slice length')
    return tuple((k[:, :length].copy(), v[:, :length].copy()) for k, v in cache)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(full, np.concatenate(parts), atol=1e-12)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

把实现与以下测试放进同一文件执行；测试覆盖正确性，不是生产环境的性能基准。

```python
def test():
    ids = [1, 4, 2, 7, 3, 8]
    model = TinyTransformer(seed=7, layers=3)
    full, _ = model.forward(ids)
    cache = None
    parts = []
    for token in ids:
        logits, cache = model.forward([token], cache)
        parts.append(logits)
    assert np.allclose(full, np.concatenate(parts), atol=1e-12)
    prefix, cache = model.forward(ids[:3])
    suffix, extended = model.forward(ids[3:], cache)
    assert np.allclose(prefix, full[:3], atol=1e-12)
    assert np.allclose(suffix, full[3:], atol=1e-12)
    assert all(k.shape == (1, 6, 4) for k, _ in extended)
    snapshot = tuple((k.copy(), v.copy()) for k, v in cache)
    branch_a, _ = model.forward([5, 9], cache)
    branch_b, _ = model.forward([6, 10], cache)
    assert np.allclose(branch_a, model.forward(ids[:3] + [5, 9])[0][3:])
    assert np.allclose(branch_b, model.forward(ids[:3] + [6, 10])[0][3:])
    assert all(
        np.array_equal(a, b)
        for pair, saved in zip(cache, snapshot)
        for a, b in zip(pair, saved)
    )
    # A future token must not change prefix hidden states at any layer.
    altered, _ = model.forward(ids[:-1] + [12])
    assert np.allclose(altered[:-1], full[:-1])
    assert all(k.shape[1] == 2 for k, _ in slice_cache(cache, 2))


if __name__ == '__main__':
    test()
```

### 复杂度与追问

设层数 L、后缀长度 T、前缀长度 S、宽度 D。投影与 MLP 约为 $O(LTD^2)$，attention 约为 $O(LT(S+T)D)$，持久 KV 空间是 $O(LH_{kv}(S+T)d)$。NumPy concat 会复制旧 cache，所以这里只验证前缀计算被省下，零拷贝和 GPU 性能还需另做实现与验收。

只存 KV、prompt 完整命中时，还要通过第⑦题的重放计划取末 token logits。`cache` 也必须对应原模型与位置语义，raw 张量接口无法识别模型混用，第⑤及⑧题会补上这层约束。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[openai-kv-cache-impl]]：OpenAI 面经版，单层 `mha` 加 cache，验收同样是有/无 cache 对齐。
- [[coding-rope-cache]]：单独练 RoPE 表和从 `cache_len` 起算的 `position_ids`。
- [[kv-prefix-reuse-plan]]：第⑦题，完整命中时为什么要重放末 token。
- [[kv-prefix-engine]]：第⑧题，把这里的 forward 和 radix tree 接成能少算前缀的推理循环。
