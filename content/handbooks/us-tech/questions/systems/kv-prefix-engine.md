---
id: kv-prefix-engine
section: systems
order: 38
level: S
title: "KV Prefix ⑧：把 Radix Tree 接进 Transformer——可运行 Prefix Engine"
quick: "完整走一遍：查前缀、恢复每层 KV、只算后缀、greedy decode、把新 KV 插回树，并和 cold run 对比 token、每层 KV 和少算的 token 数。"
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
  - title: "SGLang prefix matching and insertion lifecycle"
    url: https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/mem_cache/radix_cache.py
    type: primary
  - title: "Transformer architecture"
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

## 完整编程练习（手册原创实现版）

> 这是为理解开源机制写的独立练习，不是某家公司确认过的原题，也不是 SGLang / vLLM 源码的逐字翻译；接口、简化条件和测试由手册定义。Python 3 + NumPy，CPU 上验证数值和状态语义，不报告 GPU 吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

- `TinyTransformer(seed, layers, vocab, width, heads, kv_heads)`：冻结权重的单请求因果模型，包含 RMSNorm、RoPE、GQA 和门控 MLP。`forward(token_ids, cache=None) -> (logits, new_cache)`，`cache` 是每层一个 `(K, V)`，形状 `[kv_heads, 已缓存长度, head_dim]`。模型的 `fingerprint` 是配置和全部权重的哈希，`computed_tokens` 累计送进 forward 的 token 数。
- `RadixCache`：按 token 粒度压缩边的前缀树，每个 token 对应一个不可变的 KV 句柄。`match(tokens, namespace) -> (命中长度, 句柄)`，`insert(tokens, values, namespace) -> 已存在的前缀长度`；重复前缀沿用树里已有的句柄。
- `plan_reuse(prompt_length, matched_tokens, page_size, chunk_budget, need_last_logits) -> (可复用长度, chunks)`：按页对齐命中长度；完全命中时退回最后一个 token，因为只有 KV 算不出最后一个位置的 logits。剩下的后缀按 `chunk_budget` 切块。
- `PrefixEngine(model).generate(prompt, new_tokens, scope="default", chunk_budget=1024) -> (生成的 token, 统计)`：namespace 是 `(模型指纹, scope)`。查命中后恢复各层 KV，按 chunk 只 forward 未复用的后缀，再 greedy 生成 `new_tokens` 个 token（$\ge 0$，没有 EOS 提前停止）。每个生成的 token 也送进一次 forward，这样插回树的 cache 覆盖 prompt 加全部生成文本。
- 统计里有 `matched`（树上命中长度）、`reused`（实际复用长度）、`prefill_computed`（prompt 里重新计算的 token 数）、`total_computed`（这次调用 forward 的总 token 数）。

### 输入输出示例

```text
先 generate([1, 2, 3, 4], 2)，树里存下 [1, 2, 3, 4] + 2 个生成 token

generate([1, 2, 3, 7, 8], 3, chunk_budget=1)
-> 命中并复用 3 个 token，prefill 只算 [7, 8] 两个，再加 3 次 decode，共计算 5 个
-> cold run（空树）要算 5 + 3 = 8 个
-> 生成的 token 和每一层 KV 都与 cold run 一致

generate([1, 2], 2)
-> 树上命中 2 个（在一条边的中间），但只复用 1 个，重算最后一个 token 拿 logits
```

### 解题思路与正确性

前缀缓存的价值要体现在送进 forward 的 token 变少，而不只是树返回了一个命中长度。所以每层的 KV 恢复出来后，模型只接收未复用的 token；位置从已缓存长度开始，RoPE 和因果 mask 都按绝对位置算，结果和从头计算一致。

生成的 token 也要插回树里，下一轮对话带着上一轮的回答来时才能继续命中。完全命中时仍通过 `plan_reuse` 重放最后一个 token，而不是试图从 KV 里凭空得到最后的 logits。

namespace 里的模型指纹隔离不同权重：即使两个引擎共享一棵树，也不会用错 KV。scope 隔离租户或会话的共享策略。

### 完整参考实现（Python 3）

```python
import hashlib

import numpy as np


class TinyTransformer:
    """CPU 参考模型：RMSNorm、RoPE、GQA 和门控 MLP，层数 >= 1，权重冻结。"""

    def __init__(self, seed=0, layers=2, vocab=19, width=8, heads=2, kv_heads=1):
        if layers < 1 or width % heads or heads % kv_heads or (width // heads) % 2:
            raise ValueError(
                f"bad head geometry: layers={layers}, width={width}, heads={heads}, kv_heads={kv_heads}")
        self.layers = layers
        self.heads = heads
        self.kv_heads = kv_heads
        self.width = width
        self.head_dim = width // heads
        rng = np.random.default_rng(seed)

        def weight(rows, cols):
            return rng.normal(scale=0.2, size=(rows, cols))

        kv_width = kv_heads * self.head_dim
        self.embed = weight(vocab, width)
        self.output = weight(width, vocab)
        self.weights = []
        for _ in range(layers):
            self.weights.append({
                "q": weight(width, width),
                "k": weight(width, kv_width),
                "v": weight(width, kv_width),
                "o": weight(width, width),
                "gate": weight(width, 2 * width),
                "up": weight(width, 2 * width),
                "down": weight(2 * width, width),
            })
        # 冻结的配置和权重决定 cache 的 namespace
        arrays = [self.embed, self.output]
        arrays += [layer[name] for layer in self.weights for name in sorted(layer)]
        digest = hashlib.sha256(str((layers, width, heads, kv_heads)).encode())
        for array in arrays:
            array.flags.writeable = False
            digest.update(array.tobytes())
        self.fingerprint = digest.hexdigest()
        self.computed_tokens = 0

    @staticmethod
    def norm(x):
        return x / np.sqrt(np.mean(x * x, axis=-1, keepdims=True) + 1e-6)

    @staticmethod
    def rotate(x, start):
        """对 [heads, T, head_dim] 做 RoPE，位置从 start 开始。"""
        head_dim = x.shape[-1]
        positions = np.arange(start, start + x.shape[1])[:, None]
        angle = positions * 10000.0 ** (-np.arange(0, head_dim, 2) / head_dim)  # [T, head_dim/2]
        even = x[..., 0::2]
        odd = x[..., 1::2]
        out = np.empty_like(x)
        out[..., 0::2] = even * np.cos(angle) - odd * np.sin(angle)
        out[..., 1::2] = even * np.sin(angle) + odd * np.cos(angle)
        return out

    def _cached_length(self, cache):
        if len(cache) != self.layers:
            raise ValueError(f"expected one KV pair per layer ({self.layers}), got {len(cache)}")
        lengths = set()
        for k, v in cache:
            if (k.ndim != 3 or k.shape != v.shape or k.shape[0] != self.kv_heads
                    or k.shape[-1] != self.head_dim):
                raise ValueError(f"bad cache shape: K {k.shape}, V {v.shape}")
            lengths.add(k.shape[1])
        if len(lengths) != 1:
            raise ValueError(f"layer cache lengths disagree: {sorted(lengths)}")
        return lengths.pop()

    def forward(self, token_ids, cache=None):
        """token_ids: 非空整数序列；cache: 每层 (K, V)，[kv_heads, old, head_dim]。

        返回 (logits [T, vocab], 每层追加后的 (K, V))。
        """
        ids = np.asarray(token_ids)
        if ids.ndim != 1 or ids.dtype.kind not in "iu" or not len(ids):
            raise ValueError("nonempty 1-D integer token sequence required")
        if (ids < 0).any() or (ids >= len(self.embed)).any():
            raise ValueError(f"token ids must be in [0, {len(self.embed)})")
        old = 0 if cache is None else self._cached_length(cache)
        num_new = len(ids)
        total = old + num_new
        group = self.heads // self.kv_heads
        x = self.embed[ids].copy()  # [T, width]
        new_cache = []
        for layer, w in enumerate(self.weights):
            z = self.norm(x)
            q = (z @ w["q"]).reshape(num_new, self.heads, self.head_dim).transpose(1, 0, 2)
            k = (z @ w["k"]).reshape(num_new, self.kv_heads, self.head_dim).transpose(1, 0, 2)
            v = (z @ w["v"]).reshape(num_new, self.kv_heads, self.head_dim).transpose(1, 0, 2)
            q = self.rotate(q, old)
            k = self.rotate(k, old)
            if cache is not None:
                k = np.concatenate((cache[layer][0], k), axis=1)  # [kv_heads, total, head_dim]
                v = np.concatenate((cache[layer][1], v), axis=1)
            new_cache.append((k, v))
            k_rep = np.repeat(k, group, axis=0)  # [heads, total, head_dim]
            v_rep = np.repeat(v, group, axis=0)
            scores = (q @ k_rep.swapaxes(-1, -2)) / np.sqrt(self.head_dim)  # [heads, T, total]
            allowed = np.arange(total)[None, :] <= (old + np.arange(num_new))[:, None]
            scores = np.where(allowed[None], scores, -np.inf)
            probs = np.exp(scores - scores.max(axis=-1, keepdims=True))
            probs /= probs.sum(axis=-1, keepdims=True)
            attended = (probs @ v_rep).transpose(1, 0, 2).reshape(num_new, self.width)
            x += attended @ w["o"]
            z = self.norm(x)
            gate = z @ w["gate"]
            # 数值稳定的 sigmoid，只用于 SiLU 门控
            exp_neg_abs = np.exp(-np.abs(gate))
            sigmoid = np.where(gate < 0, exp_neg_abs / (1 + exp_neg_abs), 1 / (1 + exp_neg_abs))
            x += (gate * sigmoid * (z @ w["up"])) @ w["down"]
        self.computed_tokens += num_new
        return self.norm(x) @ self.output, tuple(new_cache)


def slice_cache(cache, length):
    """取每层 KV 的前 length 个位置（复制）。"""
    if length < 0 or any(length > k.shape[1] for k, _ in cache):
        raise ValueError(f"cannot slice cache to length {length}")
    return tuple((k[:, :length].copy(), v[:, :length].copy()) for k, v in cache)


class Node:
    def __init__(self, edge=(), values=(), parent=None):
        self.edge = tuple(edge)      # 这条边上的 token
        self.values = tuple(values)  # 每个 token 一个 KV 句柄
        self.parent = parent
        self.children = {}           # 首 token -> 子节点
        self.locks = 0
        self.used = 0


class RadixCache:
    """token 粒度的压缩前缀树。值是不透明、不可变的 KV 句柄。"""

    def __init__(self):
        self.roots = {}  # namespace -> 根节点
        self.clock = 0

    def root(self, namespace):
        return self.roots.setdefault(namespace, Node())

    def touch(self, node):
        self.clock += 1
        node.used = self.clock

    @staticmethod
    def split(child, length):
        """把 child 的边在 length 处切开，返回新的中间节点。"""
        if not 0 < length < len(child.edge):
            raise ValueError(f"split point {length} must be inside an edge of length {len(child.edge)}")
        parent = child.parent
        mid = Node(child.edge[:length], child.values[:length], parent)
        # 正在使用的 lease 仍挂在原节点对象上，通过父节点链释放
        mid.locks = child.locks
        mid.used = child.used
        parent.children[mid.edge[0]] = mid
        child.edge = child.edge[length:]
        child.values = child.values[length:]
        child.parent = mid
        mid.children[child.edge[0]] = child
        return mid

    @staticmethod
    def _common_length(edge, tokens, offset):
        count = 0
        while (count < len(edge) and offset + count < len(tokens)
               and edge[count] == tokens[offset + count]):
            count += 1
        return count

    def walk(self, tokens, namespace, split_boundary=False):
        """沿树匹配 tokens，返回 (命中长度, 命中的句柄, 停下的节点)。"""
        tokens = tuple(tokens)
        node = self.root(namespace)
        offset = 0
        values = []
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                break
            count = self._common_length(child.edge, tokens, offset)
            values.extend(child.values[:count])
            offset += count
            if count < len(child.edge):
                if count and split_boundary:
                    node = self.split(child, count)
                break
            node = child
        return offset, tuple(values), node

    def match(self, tokens, namespace="default"):
        length, values, _ = self.walk(tokens, namespace)
        return length, values

    def insert(self, tokens, values, namespace="default"):
        """插入 tokens 及其句柄；返回树里已存在的前缀长度，调用方可丢弃这部分重复句柄。"""
        tokens = tuple(tokens)
        values = tuple(values)
        if len(tokens) != len(values):
            raise ValueError(f"need one KV handle per token: {len(tokens)} tokens, {len(values)} handles")
        node = self.root(namespace)
        offset = 0
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                child = Node(tokens[offset:], values[offset:], node)
                node.children[child.edge[0]] = child
                self.touch(child)
                return offset
            count = self._common_length(child.edge, tokens, offset)
            if count < len(child.edge):
                child = self.split(child, count)
            offset += count
            node = child
            self.touch(node)
        return offset

    def validate(self):
        """检查树的结构不变量，返回树里存的 token 总数。"""
        count = 0

        def visit(node):
            nonlocal count
            for first, child in node.children.items():
                assert child.parent is node
                assert child.edge
                assert first == child.edge[0]
                assert len(child.edge) == len(child.values)
                count += len(child.edge)
                visit(child)

        for root in self.roots.values():
            visit(root)
        return count


def plan_reuse(prompt_length, matched_tokens, page_size=1, chunk_budget=4,
               need_last_logits=True):
    """返回 (可复用长度, 待计算的 [start, end) chunks)。完全命中时退回最后一个 token。"""
    params = (prompt_length, matched_tokens, page_size, chunk_budget)
    if any(type(value) is not int for value in params):
        raise ValueError(f"integer parameters required, got {params}")
    if prompt_length < 1 or not 0 <= matched_tokens <= prompt_length:
        raise ValueError(f"bad lengths: prompt={prompt_length}, matched={matched_tokens}")
    if min(page_size, chunk_budget) < 1:
        raise ValueError(f"page_size and chunk_budget must be >= 1, got {page_size}, {chunk_budget}")
    reusable = matched_tokens // page_size * page_size
    if need_last_logits and reusable == prompt_length:
        # 只有 KV 得不到最后的 hidden state / logits，至少重放最后一个 token
        reusable = (prompt_length - 1) // page_size * page_size
    chunks = []
    for start in range(reusable, prompt_length, chunk_budget):
        chunks.append((start, min(prompt_length, start + chunk_budget)))
    return reusable, tuple(chunks)


class PrefixEngine:
    """把 RadixCache 接到 TinyTransformer 上：复用前缀 KV，只算后缀，生成后插回树。"""

    def __init__(self, model):
        self.model = model
        self.index = RadixCache()

    @staticmethod
    def token_values(cache):
        """把每层 KV 拆成每个 token 一个只读句柄：tuple(每层 (k, v))。"""
        seq_len = cache[0][0].shape[1]
        handles = []
        for pos in range(seq_len):
            layers = []
            for k, v in cache:
                pair = (k[:, pos].copy(), v[:, pos].copy())
                for array in pair:
                    array.flags.writeable = False
                layers.append(pair)
            handles.append(tuple(layers))
        return tuple(handles)

    @staticmethod
    def restore(values):
        """把 token 句柄拼回每层 (K, V)；没有句柄时返回 None。"""
        if not values:
            return None
        num_layers = len(values[0])
        return tuple(
            (np.stack([token[layer][0] for token in values], axis=1),
             np.stack([token[layer][1] for token in values], axis=1))
            for layer in range(num_layers)
        )

    def generate(self, prompt, new_tokens, scope="default", chunk_budget=1024):
        """复用前缀 KV 后 greedy 生成 new_tokens 个 token，返回 (token 列表, 统计)。"""
        prompt = tuple(prompt)
        vocab = len(self.model.embed)
        if not prompt or any(type(token) is not int or not 0 <= token < vocab for token in prompt):
            raise ValueError(f"prompt must be a nonempty sequence of token ids in [0, {vocab})")
        if type(new_tokens) is not int or new_tokens < 0:
            raise ValueError(f"new_tokens must be a non-negative int, got {new_tokens!r}")
        namespace = (self.model.fingerprint, scope)
        hit, values = self.index.match(prompt, namespace)
        reused, chunks = plan_reuse(len(prompt), hit, 1, chunk_budget, True)
        cache = self.restore(values[:reused])
        before = self.model.computed_tokens
        for start, end in chunks:
            logits, cache = self.model.forward(prompt[start:end], cache)
        generated = []
        for _ in range(new_tokens):
            token = int(np.argmax(logits[-1]))
            generated.append(token)
            # 选出的 token 也送进 forward，保证插回树的 KV 覆盖所有公开的 token
            logits, cache = self.model.forward([token], cache)
        sequence = prompt + tuple(generated)
        self.index.insert(sequence, self.token_values(cache), namespace)
        stats = {
            "matched": hit,
            "reused": reused,
            "prefill_computed": len(prompt) - reused,
            "total_computed": self.model.computed_tokens - before,
        }
        return generated, stats
```

### 可执行测试

```python
model = TinyTransformer(seed=8, layers=3)
engine = PrefixEngine(model)
engine.generate([1, 2, 3, 4], 2)

# 部分命中：复用 3 个 token，prefill 只算 2 个，加 3 次 decode 共 5 个
prompt = [1, 2, 3, 7, 8]
actual, stats = engine.generate(prompt, 3, chunk_budget=1)
cold = PrefixEngine(TinyTransformer(seed=8, layers=3))
expected, cold_stats = cold.generate(prompt, 3)
assert actual == expected
assert stats["reused"] == 3
assert stats["prefill_computed"] == 2
assert stats["total_computed"] == 5
assert cold_stats["total_computed"] == 8

# 树里每一层的 KV 都等于完整重算，而不只是 greedy token 一致
sequence = prompt + actual
_, values = engine.index.match(sequence, (model.fingerprint, "default"))
cached = engine.restore(values)
_, reference = model.forward(sequence)
for cached_layer, fresh_layer in zip(cached, reference):
    for cached_array, fresh_array in zip(cached_layer, fresh_layer):
        assert np.allclose(cached_array, fresh_array, atol=1e-12)

# 更短的 prompt 在边中间完全命中，但仍要重算最后一个 token 拿 logits
output, stats = engine.generate([1, 2], 2)
gold, _ = cold.generate([1, 2], 2)
assert output == gold
assert stats["matched"] == 2
assert stats["reused"] == 1
assert stats["prefill_computed"] == 1

# 不同 scope 互不复用
_, stats = engine.generate([1, 2, 3], 0, scope="other-tenant")
assert stats["reused"] == 0

# 两个模型共享一棵树也安全，因为 namespace 里有冻结模型的哈希
other = PrefixEngine(TinyTransformer(seed=99, layers=3))
other.index = engine.index
_, stats = other.generate([1, 2, 3], 0)
assert stats["reused"] == 0

# plan_reuse：按页对齐，完全命中时退回最后一页
assert plan_reuse(10, 7, page_size=4, chunk_budget=4) == (4, ((4, 8), (8, 10)))
assert plan_reuse(8, 8, page_size=4, chunk_budget=8) == (4, ((4, 8),))
assert plan_reuse(8, 8, need_last_logits=False) == (8, ())

# 非法输入
for bad_call in (lambda: engine.generate([], 1),
                 lambda: engine.generate([1, 99], 1),
                 lambda: engine.generate([1], -1),
                 lambda: plan_reuse(3, 4)):
    try:
        bad_call()
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")

# 树结构不变量成立
assert engine.index.validate() > 0
```

### 复杂度与追问

设 prompt 长度为 $P$、命中长度为 $h$、生成长度为 $G$、层数为 $L$。radix 查找是 $O(P)$；恢复连续 KV 要复制命中的 $h$ 个位置，拆成句柄存进树也会复制数组，所以这是数值和控制流的参考，不是零拷贝的生产引擎。省下来的是前缀那 $h$ 个 token 在各层的投影、注意力和 MLP 计算，测试里直接断言了实际的计算计数。物理页的 COW 和分段读取分别在第④、⑥题里给出。

- 追问「还缺什么」：模型并发读写、多请求调度、GPU 分页 kernel、异步淘汰都不在这个单线程参考里。
- 追问「怎么扩展」：用第④题的页池替换 `restore`，结合第⑥题按页 / 按段读取，再用第③题的 lease 保护运行中的请求。每改一步都必须重新验证和完整重算等价。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口，本题是 8 道里的收尾集成。
- [[kv-prefix-transformer]]：第①题，提供这里用到的多层 forward 和每层 KV 接口。
- [[kv-prefix-radix]]：第②题，这里查前缀、插回新 KV 用的就是那棵树。
- [[kv-prefix-reuse-plan]]：第⑦题，决定命中之后哪些 token 要重放、后缀怎么切 chunk。
- [[kv-prefix-paged-cow]]：第④题，把这里的连续 cache 换成共享页池时要用。
- [[kv-prefix-segmented-attention]]：第⑥题，不拼接前缀、直接分段读 KV 的数值原语。
