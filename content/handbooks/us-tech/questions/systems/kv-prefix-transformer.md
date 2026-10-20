---
id: kv-prefix-transformer
section: systems
order: 31
level: S
title: "KV Prefix ①：多层 Transformer 的 prefill、decode 与前缀分叉"
quick: "实际写出每层 K/V 的复用路径，带 RoPE、GQA、残差和门控 MLP；验证整段重算、逐 token decode、分块 prefill 的 logits 一致。"
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "Attention Is All You Need"
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 完整编程练习（手册原创实现版）

本题是为理解开源机制而编写的独立练习，不是某家公司的已确认原题，也不是SGLang/vLLM源码逐字翻译。接口、简化条件和测试由手册定义。依赖Python 3与NumPy，使用CPU测试数值及状态语义，不报告GPU吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

实现 `TinyTransformer.forward(token_ids,cache=None)` 和 `slice_cache`。这是确定性、单请求的 NumPy float64 多层 decoder-only 模型：词嵌入、pre-RMSNorm、RoPE、GQA、attention 输出投影、残差、门控 MLP、最终归一化与词表 logits，禁用 dropout。输入非空合法整数 token，默认词表19、层数2、宽8、query heads2、KV heads1；维度关系合法。每层 cache 为 K/V 各 `[Hkv,S,d]`，全部层长度必须相同。返回新 token 的 `[T,V]` logits 和覆盖旧前缀及新后缀的每层 cache。模型权重冻结后不得改变；原 cache 不得被修改。

### 输入输出示例

输入 `[1,4,2,7,3,8]`：一次 forward 得到6行 logits；先算前3项，再用 cache 只算后3项，后缀 logits 必须等于完整计算的第3至5行。两个不同后缀从同一前缀分叉，不得互相污染。

### 解题思路与正确性

每一层都要复用该层的 K/V，而非复用第一层或仅保存 token ID。新 Q/K 的 RoPE 位置从已有 cache 长度开始，旧 K 已经旋转，不能二次旋转。矩形因果 mask 使用绝对条件 `key_pos <= old_len + query_offset`。在同一模型、位置与注意力语义下，归纳到每一层即可得到与完整前向一致的后缀隐藏状态。

### 完整参考实现（Python 3）

```python
import hashlib
import numpy as np


class TinyTransformer:
    """Two-or-more-layer CPU reference: RMSNorm, RoPE, GQA and gated MLP."""
    def __init__(self, seed=0, layers=2, vocab=19, width=8, heads=2, kv_heads=1):
        if layers < 1 or width % heads or heads % kv_heads or (width//heads) % 2:
            raise ValueError('head geometry')
        self.layers, self.heads, self.kv_heads = layers, heads, kv_heads
        self.width, self.d = width, width//heads
        rng = np.random.default_rng(seed)
        def weight(a, b):
            return rng.normal(scale=.2, size=(a, b))
        self.embed = weight(vocab, width)
        self.output = weight(width, vocab)
        self.weights = []
        for _ in range(layers):
            self.weights.append(dict(q=weight(width, width),
                                     k=weight(width, kv_heads*self.d),
                                     v=weight(width, kv_heads*self.d),
                                     o=weight(width, width),
                                     gate=weight(width, 2*width),
                                     up=weight(width, 2*width),
                                     down=weight(2*width, width)))
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
        return x / np.sqrt(np.mean(x*x, axis=-1, keepdims=True)+1e-6)

    @staticmethod
    def rotate(x, start):
        d = x.shape[-1]
        angle = np.arange(start, start+x.shape[1])[:, None] * 10000.**(-np.arange(0, d, 2)/d)
        even, odd = x[..., 0::2], x[..., 1::2]
        out = np.empty_like(x)
        out[..., 0::2] = even*np.cos(angle)-odd*np.sin(angle)
        out[..., 1::2] = even*np.sin(angle)+odd*np.cos(angle)
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
                if k.ndim != 3 or k.shape != v.shape or k.shape[0] != self.kv_heads or k.shape[-1] != self.d:
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
            q = self.rotate((z@w['q']).reshape(t, self.heads, self.d).transpose(1, 0, 2), old)
            k = self.rotate((z@w['k']).reshape(t, self.kv_heads, self.d).transpose(1, 0, 2), old)
            v = (z@w['v']).reshape(t, self.kv_heads, self.d).transpose(1, 0, 2)
            if cache is not None:
                k = np.concatenate((cache[layer][0], k), axis=1)
                v = np.concatenate((cache[layer][1], v), axis=1)
            new_cache.append((k, v))
            kr, vr = (np.repeat(a, self.heads//self.kv_heads, axis=0) for a in (k, v))
            scores = (q@kr.swapaxes(-1, -2))/np.sqrt(self.d)
            allowed = np.arange(old+t)[None, :] <= (old+np.arange(t))[:, None]
            scores = np.where(allowed[None], scores, -np.inf)
            p = np.exp(scores-scores.max(axis=-1, keepdims=True))
            p /= p.sum(axis=-1, keepdims=True)
            attended = (p@vr).transpose(1, 0, 2).reshape(t, self.width)
            x += attended@w['o']
            z = self.norm(x)
            gate = z@w['gate']
            # Stable sigmoid, used only in the SiLU gate.
            e = np.exp(-np.abs(gate))
            sigmoid = np.where(gate < 0, e/(1+e), 1/(1+e))
            x += (gate*sigmoid*(z@w['up']))@w['down']
        self.computed_tokens += t
        return self.norm(x)@self.output, tuple(new_cache)


def slice_cache(cache, length):
    if length < 0 or any(length > k.shape[1] for k, _ in cache):
        raise ValueError('cache slice length')
    return tuple((k[:, :length].copy(), v[:, :length].copy()) for k, v in cache)
```

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
    assert np.allclose(branch_a, model.forward(ids[:3]+[5, 9])[0][3:])
    assert np.allclose(branch_b, model.forward(ids[:3]+[6, 10])[0][3:])
    assert all(np.array_equal(a, b) for pair, saved in zip(cache, snapshot) for a, b in zip(pair, saved))
    # A future token must not change prefix hidden states at any layer.
    altered, _ = model.forward(ids[:-1]+[12])
    assert np.allclose(altered[:-1], full[:-1])
    assert all(k.shape[1] == 2 for k, _ in slice_cache(cache, 2))

if __name__ == '__main__':
    test()
```

### 复杂度与追问

设层数L、后缀T、前缀S、宽D：投影与MLP约为 $O(LTD^2)$，注意力约为 $O(LT(S+T)D)$，持久KV空间 $O(LH_{kv}(S+T)d)$。NumPy concat会复制旧cache；本题证明少算前缀，不声称零拷贝或GPU性能。

如果只存了KV，完整命中时能否直接拿到下一token logits？不能；看第⑦题的重放计划。`cache`必须与生成它的模型和位置语义对应，raw张量接口本身不能识别模型混用，第⑤及⑧题补这层约束。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[openai-kv-cache-impl]]：OpenAI 面经版，单层 `mha` 加 cache，验收同样是有/无 cache 对齐。
- [[coding-rope-cache]]：单独练 RoPE 表和从 `cache_len` 起算的 `position_ids`。
- [[kv-prefix-reuse-plan]]：第⑦题，完整命中时为什么要重放末 token。
- [[kv-prefix-engine]]：第⑧题，把这里的 forward 和 radix tree 接成能少算前缀的推理循环。
