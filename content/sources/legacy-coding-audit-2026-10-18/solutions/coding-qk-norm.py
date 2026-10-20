import torch


def rmsnorm_last(x, weight, eps=1e-6):
    """沿最后一维 d 做 RMSNorm（统计量用 fp32 算），weight 为 [d] 或 None（不缩放）。"""
    x_fp32 = x.float()
    inv_rms = torch.rsqrt(x_fp32.pow(2).mean(dim=-1, keepdim=True) + eps)
    normed = (x_fp32 * inv_rms).to(x.dtype)
    return normed if weight is None else normed * weight


def apply_rope(x, cos, sin):
    """对 x: [B, H, T, d] 做 RoPE，维度 (0, 1)、(2, 3)… 两两成对旋转。cos, sin: [T, d/2]。"""
    seq_len, head_dim = x.shape[-2], x.shape[-1]
    if head_dim % 2:
        raise ValueError(f"RoPE requires an even head dim, got {head_dim}")
    expected = (seq_len, head_dim // 2)
    if cos.shape != expected or sin.shape != expected:
        raise ValueError(f"cos and sin must be {expected}, "
                         f"got {tuple(cos.shape)} and {tuple(sin.shape)}")
    even, odd = x[..., 0::2], x[..., 1::2]
    rotated_even = even * cos - odd * sin
    rotated_odd = even * sin + odd * cos
    # 把两半交错拼回 [.., d]：(e0, o0, e1, o1, ...)
    return torch.stack((rotated_even, rotated_odd), dim=-1).flatten(-2)


def qk_norm_then_rope(q, k, w_q, w_k, cos, sin):
    """先各自做 QK RMSNorm，再做 RoPE。q: [B, H_q, T, d]，k: [B, H_kv, T, d]。"""
    q = rmsnorm_last(q, w_q)
    k = rmsnorm_last(k, w_k)
    return apply_rope(q, cos, sin), apply_rope(k, cos, sin)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def rope_tables(seq_len, head_dim):
    positions = torch.arange(float(seq_len))[:, None]
    inv_freq = 10000 ** (-torch.arange(0, head_dim, 2) / head_dim)
    return torch.cos(positions * inv_freq), torch.sin(positions * inv_freq)


torch.manual_seed(0)
torch.set_num_threads(1)
q = torch.randn(2, 4, 3, 4)  # H_q = 4
k = torch.randn(2, 2, 3, 4)  # H_kv = 2，Q/K 的 head 数可以不同
ones = torch.ones(4)
cos, sin = rope_tables(3, 4)

# 形状不变；单位权重下旋转不改变归一化之后的范数
q_out, k_out = qk_norm_then_rope(q, k, ones, ones, cos, sin)
assert q_out.shape == q.shape
assert k_out.shape == k.shape
assert torch.allclose(q_out.square().sum(-1),
                      rmsnorm_last(q, ones).square().sum(-1), atol=1e-5)

# 全零输入归一化后仍是 0（eps 防止除 0）
assert torch.all(rmsnorm_last(torch.zeros_like(q), ones) == 0)

# 归一化后每个 head 的 RMS 约为 1；weight=None 等价于全 1 权重
assert torch.allclose(rmsnorm_last(q, None).square().mean(-1),
                      torch.ones(2, 4, 3), atol=1e-4)
assert torch.allclose(rmsnorm_last(q, None), rmsnorm_last(q, ones))

# 位置 0 的 cos = 1、sin = 0，RoPE 不改变第一个 token
assert torch.allclose(apply_rope(q, cos, sin)[:, :, 0], q[:, :, 0])

# 顺序：gamma 全为 1 时两种顺序相同（旋转不改变 RMS），gamma 不均匀时就不同了
gamma = torch.tensor([1.0, 2.0, 0.5, 3.0])
norm_first = apply_rope(rmsnorm_last(q, ones), cos, sin)
rope_first = rmsnorm_last(apply_rope(q, cos, sin), ones)
assert torch.allclose(norm_first, rope_first, atol=1e-5)
norm_first = apply_rope(rmsnorm_last(q, gamma), cos, sin)
rope_first = rmsnorm_last(apply_rope(q, cos, sin), gamma)
assert not torch.allclose(norm_first, rope_first, atol=1e-3)

# 非法输入：head 维为奇数；cos/sin 的长度和 T 对不上
expect_value_error(apply_rope, torch.randn(1, 1, 3, 3), cos, sin)
expect_value_error(apply_rope, q, cos[:2], sin[:2])
