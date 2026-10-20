import math

import torch


def alibi_slopes(n_heads):
    """返回 [H] 的 ALiBi 斜率；非 2 的幂按原论文参考代码的交错规则补齐。"""
    if type(n_heads) is not int or n_heads < 1:
        raise ValueError(f"n_heads must be a positive int, got {n_heads!r}")

    def power_of_two_slopes(n):
        start = 2 ** (-2 ** -(math.log2(n) - 3))  # = 2^(-8/n)
        return [start ** i for i in range(1, n + 1)]

    floor = 2 ** int(math.floor(math.log2(n_heads)))
    values = power_of_two_slopes(floor)
    if floor != n_heads:
        values += power_of_two_slopes(2 * floor)[::2][: n_heads - floor]
    return torch.tensor(values, dtype=torch.float32)


def alibi_score_bias(q_pos, s_len, slopes):
    """q_pos: [T]，slopes: [H] -> bias [1, H, T, S]；未来位置为 -inf。"""
    k_pos = torch.arange(s_len)
    distance = (k_pos[None, :] - q_pos[:, None]).float()  # [T, S]，j - i
    causal = k_pos[None, :] <= q_pos[:, None]             # [T, S]
    bias = slopes[:, None, None] * distance[None, :, :]   # [H, T, S]
    bias = bias.masked_fill(~causal[None, :, :], float("-inf"))
    return bias.unsqueeze(0)


def decode_alibi(cache_len, slopes):
    """单步 decode 的偏置 [1, H, 1, cache_len + 1]；新 token 的位置是 cache_len。"""
    q_pos = torch.tensor([cache_len])
    return alibi_score_bias(q_pos, cache_len + 1, slopes)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# 非 2 的幂：先 2 头的斜率，再从 4 头序列隔一个取
assert torch.allclose(alibi_slopes(3), torch.tensor([1 / 16, 1 / 256, 1 / 4]))

# 8 头：1/2, 1/4, ..., 1/256
slopes = alibi_slopes(8)
assert torch.allclose(slopes, 2.0 ** (-torch.arange(1, 9)))

# 1 头：2^-8
assert torch.allclose(alibi_slopes(1), torch.tensor([1 / 256]))

# decode 的偏置等于 prefill 的最后一行，对角线（自己）为 0
prefill = alibi_score_bias(torch.arange(3), 3, slopes)
decode = decode_alibi(2, slopes)
assert prefill.shape == (1, 8, 3, 3)
assert decode.shape == (1, 8, 1, 3)
assert torch.equal(prefill[:, :, -1:], decode)
assert torch.all(decode[:, :, :, -1] == 0)

# 距离为 -2 的偏置是 -2 * m_h
assert torch.allclose(decode[0, :, 0, 0], -2 * slopes)

# 未来位置是 -inf
assert torch.isneginf(prefill[:, :, 0, 1:]).all()

# 非法 head 数
expect_value_error(alibi_slopes, 0)
expect_value_error(alibi_slopes, 2.0)
