import torch


def swa_causal_bias(q_pos, s_len, window):
    """滑动窗口 + 因果的加性偏置 [1, 1, T, S]：q - window < k <= q 处为 0，其余为 -inf。"""
    if type(window) is not int or window < 1:
        raise ValueError(f"window must be a positive int, got {window!r}")
    query = q_pos[:, None]               # [T, 1]，绝对下标
    key = torch.arange(s_len)[None, :]   # [1, S]
    visible = (key <= query) & (key > query - window)
    bias = torch.zeros(q_pos.numel(), s_len).masked_fill(~visible, float("-inf"))
    return bias.view(1, 1, q_pos.numel(), s_len)


def prefill_swa_bias(seq_len, window):
    """prefill：T = S = seq_len。"""
    return swa_causal_bias(torch.arange(seq_len), seq_len, window)


def decode_swa_bias(cache_len, window):
    """单步 decode：新 token 的下标是 cache_len，key 长度是 cache_len + 1。"""
    return swa_causal_bias(torch.tensor([cache_len]), cache_len + 1, window)


def visible(bias):
    return torch.isfinite(bias)


# decode 的偏置等于 prefill 的最后一行
prefill = prefill_swa_bias(5, 2)
last = decode_swa_bias(4, 2)
assert prefill.shape == (1, 1, 5, 5)
assert last.shape == (1, 1, 1, 5)
assert torch.equal(visible(prefill[:, :, -1:]), visible(last))

# window=2、query 位置 4：只看 key 3 和 4
assert torch.equal(visible(last[0, 0, 0]), torch.tensor([0, 0, 0, 1, 1], dtype=torch.bool))

# window=1：只看自己
assert torch.equal(visible(prefill_swa_bias(3, 1)[0, 0]), torch.eye(3, dtype=torch.bool))

# 窗口不小于序列长度时退化成普通因果
causal = torch.ones(4, 4, dtype=torch.bool).tril()
assert torch.equal(visible(prefill_swa_bias(4, 10)[0, 0]), causal)

# 每行可见的 key 数是 min(i + 1, window)
counts = visible(prefill_swa_bias(6, 3)[0, 0]).sum(-1)
assert counts.tolist() == [1, 2, 3, 3, 3, 3]

# 可见位置是 0，不是别的值
assert torch.all(last[visible(last)] == 0)

# window 必须为正
try:
    prefill_swa_bias(3, 0)
except ValueError:
    pass
else:
    raise AssertionError("window=0 accepted")
