---
id: kv-prefix-segmented-attention
section: systems
order: 36
level: S
title: "KV Prefix ⑥：共享 Prefix + 私有 Suffix 的分段 Attention"
quick: "不先 concat 公共前缀，不物化重复 KV heads：分别读共享 prefix 和各请求 suffix，用在线 max、指数和及输出累计量合并为同一个 softmax。"
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
  - title: "FlashAttention: exact attention via online softmax"
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: "PagedAttention paper"
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

## 完整编程练习（手册原创实现版）

> 这是为理解开源推理引擎机制而写的独立练习，不是哪家公司确认过的原题，也不是 SGLang / vLLM 源码的逐字翻译；接口、简化条件和测试由手册定义。Python 3 + NumPy，CPU 上验证数值和状态语义，不报告 GPU 吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

- `segmented_attention(q, segments, q_positions)`：把若干段 KV 合并成一次因果 attention，返回 `[B, Hq, T, d]`。
- `q` 是 `[B, Hq, T, d]`；`q_positions` 是 `[B, T]`，给出每个 query 的绝对位置。
- `segments` 里每段是 `(K, V, start, key_valid)`。`K`、`V` 是 `[B 或 1, Hkv, S, d]`，batch 维为 1 表示这段是各请求共享的 prefix；`start` 是该段第一个 key 的绝对位置；`key_valid` 是 `None` 或 `[B 或 1, S]` 的布尔数组。`Hq` 必须是 `Hkv` 的整数倍。
- 所有段按绝对位置拼起来，构成一组互不重叠的真实 KV。段可以为空，遍历顺序可以任意。
- 因果规则：key 的位置不超过 query 的位置才可见。某个 query 一个可见 key 都没有时，输出 0。
- 实现里不允许把共享 prefix 按 B 复制，也不允许把 prefix 和 suffix 拼成一份完整 KV。形状不合法时抛 `ValueError`。

### 输入输出示例

```text
3 条请求共享 3 个 token 的 prefix（位置 0..2），各自有 2 个 token 的 suffix（位置 3..4）
query 位置 = [3, 4]

位置 3 的 query：能看 prefix 和 suffix 的位置 3，看不到 suffix 的位置 4
把 prefix 再拆成 [0] 和 [1, 2] 两段，或倒过来遍历各段 -> 结果和 dense attention 一致
```

### 解题思路与正确性

不能对每段分别做 softmax 再平均，因为每段的归一化分母不同。正确做法是在线 softmax：每个 query 维护三样东西，当前见过的最大分数 `m`、按 `m` 平移后的指数和 `l`、按同样方式加权的 V 之和 `acc`。

读到新的一段时，先算出新的最大值 `m'`，把旧的 `l` 和 `acc` 都乘上 $e^{m-m'}$ 换到新的基准下，再加上这一段的贡献。所有段处理完后，`acc / l` 就是对全部 key 做一次 softmax 的结果。这个合并与段的切分方式、遍历顺序都无关，所以测试里拆段、倒序都能和 dense 对照对上。

GQA 时，query head `h` 读第 `h // group` 个 KV head，不物理复制 KV。共享 prefix 的 batch 维是 1，矩阵乘法自动广播到所有请求，内存里始终只有一份。

### 完整参考实现（Python 3）

```python
import numpy as np


def segmented_attention(q, segments, q_positions):
    """把若干段 KV 合并成一次因果 attention，不拼接、不复制共享 prefix。

    q: [B, Hq, T, d]；q_positions: [B, T]，每个 query 的绝对位置。
    segments: (k, v, start, key_valid) 的列表。k, v: [B 或 1, Hkv, S, d]，
    batch 维为 1 表示各请求共享；start 是该段第一个 key 的绝对位置；
    key_valid: None 或 [B 或 1, S] 的布尔数组。返回 [B, Hq, T, d]，全屏蔽的 query 输出 0。
    """
    q = np.asarray(q, dtype=float)
    if q.ndim != 4:
        raise ValueError(f"q must be [B, Hq, T, d], got shape {q.shape}")
    batch, heads, tokens, dim = q.shape
    positions = np.asarray(q_positions)
    if positions.shape != (batch, tokens):
        raise ValueError(f"q_positions must be [{batch}, {tokens}], "
                         f"got shape {positions.shape}")

    # 每个 query 的在线 softmax 状态：当前最大值、未归一化的指数和、未归一化的加权 V
    running_max = np.full((batch, heads, tokens, 1), -np.inf)
    running_sum = np.zeros_like(running_max)
    numerator = np.zeros_like(q)

    for k, v, start, key_valid in segments:
        k = np.asarray(k, dtype=float)
        v = np.asarray(v, dtype=float)
        if (k.ndim != 4 or k.shape != v.shape or k.shape[0] not in (1, batch)
                or k.shape[1] == 0 or heads % k.shape[1] or k.shape[-1] != dim):
            raise ValueError(f"segment k/v must be [1 or {batch}, Hkv, S, {dim}] "
                             f"with {heads} % Hkv == 0, got {k.shape} and {v.shape}")
        length = k.shape[2]
        if length == 0:
            continue

        key_positions = start + np.arange(length)
        allowed = key_positions[None, None, :] <= positions[:, :, None]  # [B, T, S]
        if key_valid is not None:
            key_valid = np.asarray(key_valid, dtype=bool)
            if key_valid.shape not in ((1, length), (batch, length)):
                raise ValueError(f"key_valid must be [1 or {batch}, {length}], "
                                 f"got shape {key_valid.shape}")
            allowed &= np.broadcast_to(key_valid, (batch, length))[:, None, :]

        group = heads // k.shape[1]
        # 逐个 query head 读取对应的 KV head，不把紧凑的 KV 物理复制成 Hq 份
        for head in range(heads):
            k_head = k[:, head // group]  # [B 或 1, S, d]，batch 维为 1 时靠广播共享
            v_head = v[:, head // group]
            scores = q[:, head] @ k_head.swapaxes(-1, -2) / np.sqrt(dim)  # [B, T, S]
            scores = np.where(allowed, scores, -np.inf)

            old_max = running_max[:, head]
            new_max = np.maximum(old_max, scores.max(axis=-1, keepdims=True))
            # 到目前为止全被屏蔽的行，max 仍是 -inf，换成 0 避免 -inf - (-inf)
            shift = np.where(np.isfinite(new_max), new_max, 0.0)
            old_scale = np.exp(old_max - shift)  # 把旧统计量换到新的 max 下
            weights = np.exp(scores - shift)

            numerator[:, head] = numerator[:, head] * old_scale + weights @ v_head
            running_sum[:, head] = (running_sum[:, head] * old_scale
                                    + weights.sum(axis=-1, keepdims=True))
            running_max[:, head] = new_max

    return np.divide(numerator, running_sum, out=np.zeros_like(numerator),
                     where=running_sum > 0)
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def dense_reference(q, k, v, keep):
    """把完整 KV 显式拼出来再做普通 attention，只在测试里用作对照。"""
    scores = q @ k.swapaxes(-1, -2) / np.sqrt(q.shape[-1])
    scores = np.where(keep[:, None], scores, -np.inf)
    probs = np.exp(scores - scores.max(axis=-1, keepdims=True))
    probs /= probs.sum(axis=-1, keepdims=True)
    return probs @ v


def test():
    rng = np.random.default_rng(9)
    q = rng.normal(size=(3, 4, 2, 4))         # B=3, Hq=4, T=2, d=4
    k_prefix = rng.normal(size=(1, 2, 3, 4))  # 共享 prefix：batch 维为 1，Hkv=2，长 3
    v_prefix = rng.normal(size=(1, 2, 3, 4))
    k_suffix = rng.normal(size=(3, 2, 2, 4))  # 每条请求私有的 suffix，长 2
    v_suffix = rng.normal(size=(3, 2, 2, 4))
    positions = np.tile([3, 4], (3, 1))       # 两个 query 位于绝对位置 3 和 4
    suffix_valid = np.array([[True, True], [True, False], [False, False]])
    segments = [(k_prefix, v_prefix, 0, None), (k_suffix, v_suffix, 3, suffix_valid)]
    answer = segmented_attention(q, segments, positions)

    # 和显式拼接、显式 repeat KV heads 的 dense attention 一致
    k_full = np.concatenate((np.broadcast_to(k_prefix, (3, 2, 3, 4)), k_suffix), axis=2)
    v_full = np.concatenate((np.broadcast_to(v_prefix, (3, 2, 3, 4)), v_suffix), axis=2)
    k_full = np.repeat(k_full, 2, axis=1)
    v_full = np.repeat(v_full, 2, axis=1)
    keep = np.arange(5)[None, None, :] <= positions[:, :, None]
    keep &= np.concatenate((np.ones((3, 3), bool), suffix_valid), axis=1)[:, None, :]
    assert np.allclose(answer, dense_reference(q, k_full, v_full, keep))

    # 把 prefix 再拆成两段，或者倒过来遍历各段，结果不变
    split = [(k_prefix[:, :, :1], v_prefix[:, :, :1], 0, None),
             (k_prefix[:, :, 1:], v_prefix[:, :, 1:], 1, None),
             (k_suffix, v_suffix, 3, suffix_valid)]
    assert np.allclose(segmented_attention(q, split, positions), answer)
    assert np.allclose(segmented_attention(q, list(reversed(split)), positions), answer)

    # 空段直接跳过
    empty = (np.zeros((1, 2, 0, 4)), np.zeros((1, 2, 0, 4)), 5, None)
    assert np.allclose(segmented_attention(q, segments + [empty], positions), answer)

    # 所有 key 都被屏蔽：输出全 0
    all_masked = [(k_prefix, v_prefix, 0, np.zeros((1, 3), bool))]
    assert np.array_equal(segmented_attention(q, all_masked, positions), np.zeros_like(q))

    # 位置 4 的 suffix value 对位置 3 的 query 不可见：改大它，第一个 query 的输出不变
    poisoned = v_suffix.copy()
    poisoned[:, :, 1] += 1000
    other = segmented_attention(
        q, [(k_prefix, v_prefix, 0, None), (k_suffix, poisoned, 3, suffix_valid)], positions)
    assert np.allclose(other[:, :, 0], answer[:, :, 0])

    # 非法输入：Hq=4 不是 Hkv=3 的倍数；key_valid 长度不对；q_positions 形状不对
    bad_heads = (np.zeros((1, 3, 2, 4)), np.zeros((1, 3, 2, 4)), 0, None)
    expect_value_error(segmented_attention, q, [bad_heads], positions)
    bad_valid = (k_prefix, v_prefix, 0, np.ones((1, 2), bool))
    expect_value_error(segmented_attention, q, [bad_valid], positions)
    expect_value_error(segmented_attention, q, segments, positions[:, :1])


if __name__ == "__main__":
    test()
```

### 复杂度与追问

设 prefix 长度为 $S_p$、suffix 长度为 $S_s$。总计算量仍是 $O(BH_qT(S_p+S_s)d)$，和 dense attention 一样。额外空间只有当前段的 scores 和每个 query 的三项累计量，scores 工作区的大小由最长的一段决定。prefix 的物理 KV 只存一份；但 NumPy 广播和 CPU 上的数值模拟不能代替 GPU kernel 的性能验收。

- 追问「这和第⑧题是什么关系」：这里给出的是避免拼接公共 KV 的数值原语。第⑧题为了可读性会恢复成连续 cache，所以它证明的是前缀计算可以复用，不是端到端零拷贝。
- 追问「真要写成 GPU kernel 还差什么」：还要处理分页寻址、batch 内长度不等和 kernel 调度。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[kv-prefix-engine]]：第⑧题为了可读性仍拼接连续 cache，本题给的是不拼接的替代。
