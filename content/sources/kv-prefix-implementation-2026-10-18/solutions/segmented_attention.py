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


# === TESTS ===
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
