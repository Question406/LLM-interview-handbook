import torch
from torch import nn


class RopeCache(nn.Module):
    """按绝对位置预计算的 RoPE cos / sin 表，形状 [max_seq, dim / 2]。"""

    def __init__(self, dim, max_seq=4096, base=10000.0):
        super().__init__()
        if dim % 2 != 0:
            raise ValueError(f"RoPE dim must be even, got {dim}")
        inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))  # [D/2]
        positions = torch.arange(max_seq).float()
        freqs = torch.outer(positions, inv_freq)                              # [max_seq, D/2]
        self.register_buffer("cos", freqs.cos(), persistent=False)
        self.register_buffer("sin", freqs.sin(), persistent=False)

    def at(self, position_ids):
        """position_ids: [T] 或 [B, T]，返回同前缀形状的 (cos, sin)，最后一维 D/2。"""
        max_seq = self.cos.shape[0]
        if bool(((position_ids < 0) | (position_ids >= max_seq)).any()):
            raise ValueError(f"position_ids must be in [0, {max_seq})")
        return self.cos[position_ids], self.sin[position_ids]


def position_ids_for(cache_len, q_len, batch, device=None):
    """本步 query 的绝对位置。prefill: cache_len=0 -> 0..T-1；decode: q_len=1 -> [cache_len]。"""
    positions = torch.arange(cache_len, cache_len + q_len, device=device)
    return positions.unsqueeze(0).expand(batch, -1)  # [batch, q_len]


def apply_rope(x, cos, sin):
    """x: [B, H, T, D]；cos / sin: [T, D/2] 或 [B, T, D/2]。相邻偶奇分量成对旋转。"""
    if cos.dim() == 2:
        cos = cos[None, None, :, :]  # [1, 1, T, D/2]
        sin = sin[None, None, :, :]
    elif cos.dim() == 3:
        cos = cos[:, None, :, :]     # [B, 1, T, D/2]
        sin = sin[:, None, :, :]
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    rotated_even = x_even * cos - x_odd * sin
    rotated_odd = x_even * sin + x_odd * cos
    return torch.stack((rotated_even, rotated_odd), dim=-1).flatten(-2)


def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


torch.set_num_threads(1)
torch.manual_seed(0)
rope = RopeCache(4, max_seq=8)

# 有 cache 时位置从 cache_len 开始
positions = position_ids_for(3, 2, 2)
assert torch.equal(positions, torch.tensor([[3, 4], [3, 4]]))
assert torch.equal(position_ids_for(5, 1, 1), torch.tensor([[5]]))

# [B, T] 的 position_ids 与逐条用 [T] 的结果一致
x = torch.randn(2, 3, 2, 4)
cos, sin = rope.at(positions)
rotated = apply_rope(x, cos, sin)
for b in range(2):
    cos_row, sin_row = rope.at(positions[b])
    assert torch.allclose(rotated[b:b + 1], apply_rope(x[b:b + 1], cos_row, sin_row))

# 位置 0 不旋转；旋转保持范数
cos0, sin0 = rope.at(torch.tensor([0, 0]))
assert torch.allclose(apply_rope(x, cos0, sin0), x)
assert torch.allclose(rotated.norm(dim=-1), x.norm(dim=-1), atol=1e-6)

# 点积只依赖相对位置：(5, 3) 与 (4, 2) 相同
q = torch.randn(1, 1, 1, 4)
k = torch.randn(1, 1, 1, 4)


def score(q_pos, k_pos):
    cos_q, sin_q = rope.at(torch.tensor([q_pos]))
    cos_k, sin_k = rope.at(torch.tensor([k_pos]))
    return (apply_rope(q, cos_q, sin_q) * apply_rope(k, cos_k, sin_k)).sum()


assert torch.allclose(score(5, 3), score(4, 2), atol=1e-6)

# 越界位置报错，不取模
expect_error(ValueError, rope.at, torch.tensor([-1]))
expect_error(ValueError, rope.at, torch.tensor([8]))

# 奇数维度报错
expect_error(ValueError, RopeCache, 3)
