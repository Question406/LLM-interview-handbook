import torch


def rope_angles(dim, seqlen, base=10000.0, device=None):
    """返回 cos, sin，形状 [seqlen, dim/2]；第 i 对维度的频率是 base^(-2i/dim)。"""
    if dim <= 0 or dim % 2 != 0:
        raise ValueError(f"RoPE needs a positive even head dim, got {dim}")
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, device=device).float() / dim))
    positions = torch.arange(seqlen, device=device).float()
    freqs = torch.outer(positions, inv_freq)  # [T, D/2]
    return torch.cos(freqs), torch.sin(freqs)


def apply_rope(x, cos, sin):
    """x: [B, H, T, D]；cos, sin: [T, D/2]。偶奇相邻两维成对旋转。"""
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    cos = cos[None, None, :, :]
    sin = sin[None, None, :, :]
    y_even = x_even * cos - x_odd * sin
    y_odd = x_even * sin + x_odd * cos
    return torch.stack((y_even, y_odd), dim=-1).flatten(-2)


def decode_rope(q, k, cos, sin, pos):
    """decode 一步：pos 是已有 cache 长度，取这一行的 cos/sin 旋转 q、k（不要用 0）。"""
    if not 0 <= pos < cos.shape[0]:
        raise ValueError(f"position {pos} is outside the RoPE table of length {cos.shape[0]}")
    cos_t = cos[pos:pos + 1]
    sin_t = sin[pos:pos + 1]
    return apply_rope(q, cos_t, sin_t), apply_rope(k, cos_t, sin_t)


torch.set_num_threads(1)
torch.manual_seed(0)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


cos, sin = rope_angles(4, 8)
x = torch.randn(2, 3, 5, 4)
y = apply_rope(x, cos[:5], sin[:5])

# 位置 0 是恒等变换
assert torch.allclose(y[..., 0, :], x[..., 0, :])

# 旋转不改变范数
assert torch.allclose(y.square().sum(-1), x.square().sum(-1), atol=1e-6)

# decode 用 pos = 2 和完整序列的第 3 个位置一致
q_t, k_t = decode_rope(x[:, :, 2:3], x[:, :, 2:3], cos, sin, 2)
assert torch.allclose(q_t, y[:, :, 2:3])
assert torch.allclose(q_t, k_t)

# 点积只依赖相对位置：(m, n) = (3, 1) 和 (4, 2) 的结果相同
q_vec = torch.randn(1, 1, 1, 4).expand(1, 1, 5, 4)
k_vec = torch.randn(1, 1, 1, 4).expand(1, 1, 5, 4)
q_rot = apply_rope(q_vec, cos[:5], sin[:5])
k_rot = apply_rope(k_vec, cos[:5], sin[:5])
dot = lambda m, n: (q_rot[0, 0, m] * k_rot[0, 0, n]).sum()
assert torch.allclose(dot(3, 1), dot(4, 2), atol=1e-5)

# 奇数维和越界位置被拒绝
expect_value_error(rope_angles, 3, 8)
expect_value_error(decode_rope, x[:, :, :1], x[:, :, :1], cos, sin, 8)
