import torch
import torch.nn.functional as F


def mqa(q, k, v, attn_bias=None):
    """Multi-Query Attention：q [B, H, T, d_h]，k/v [B, 1, S, d_h] 或 [B, S, d_h] -> [B, H, T, d_h]。

    K、V 沿 head 维广播，不复制成 H 份。
    """
    if k.dim() == 3:
        k = k.unsqueeze(1)
        v = v.unsqueeze(1)
    if k.shape[1] != 1 or v.shape[1] != 1:
        raise ValueError(f"MQA expects exactly one KV head, got {k.shape[1]} and {v.shape[1]}")
    if q.shape[0] != k.shape[0] or q.shape[-1] != k.shape[-1]:
        raise ValueError(f"q {tuple(q.shape)} and k {tuple(k.shape)} disagree on batch or head dim")

    scale = q.size(-1) ** -0.5
    scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H, T, S]
    if attn_bias is not None:
        scores = scores + attn_bias
    probs = torch.softmax(scores.float(), dim=-1).to(q.dtype)  # 沿 key 维
    return torch.matmul(probs, v)                              # [B, H, T, d_h]


def mqa_projections(x, wq, wk, wv, n_heads):
    """x [B, T, D] -> q [B, H, T, d_h]，k/v [B, 1, T, d_h]；wq [D, D]，wk/wv [D, d_h]。"""
    batch, seq_len, model_dim = x.shape
    if model_dim % n_heads != 0:
        raise ValueError(f"model dim {model_dim} is not divisible by n_heads={n_heads}")
    head_dim = model_dim // n_heads
    if wk.shape != (model_dim, head_dim) or wv.shape != (model_dim, head_dim):
        raise ValueError(f"wk/wv must be [{model_dim}, {head_dim}], got {tuple(wk.shape)} and {tuple(wv.shape)}")
    q = (x @ wq).view(batch, seq_len, n_heads, head_dim).transpose(1, 2)
    k = (x @ wk).view(batch, seq_len, 1, head_dim).transpose(1, 2)
    v = (x @ wv).view(batch, seq_len, 1, head_dim).transpose(1, 2)
    return q, k, v


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(0)
x = torch.randn(2, 3, 8)
wq = torch.randn(8, 8)
wk = torch.randn(8, 2)
wv = torch.randn(8, 2)

# 投影形状：Q 有 4 个 head，K/V 只有 1 个
q, k, v = mqa_projections(x, wq, wk, wv, 4)
assert q.shape == (2, 4, 3, 2)
assert k.shape == (2, 1, 3, 2)

# 与把 K/V 显式 expand 成 H 份后的标准注意力一致
out = mqa(q, k, v)
reference = F.scaled_dot_product_attention(q, k.expand(-1, 4, -1, -1), v.expand(-1, 4, -1, -1))
assert torch.allclose(out, reference, atol=1e-5)

# 省掉 head 维的 [B, S, d_h] 输入结果相同
assert torch.allclose(mqa(q, k[:, 0], v[:, 0]), out)

# 因果 bias 与 SDPA 的 is_causal 一致
causal_bias = torch.full((3, 3), float("-inf")).triu(1)
causal_ref = F.scaled_dot_product_attention(q, k.expand(-1, 4, -1, -1), v.expand(-1, 4, -1, -1), is_causal=True)
assert torch.allclose(mqa(q, k, v, causal_bias), causal_ref, atol=1e-5)

# 非法输入：两个 KV head、wk 写成 [D, D]、D 不能整除
expect_value_error(mqa, q, k.expand(-1, 2, -1, -1), v.expand(-1, 2, -1, -1))
expect_value_error(mqa_projections, x, wq, torch.randn(8, 8), torch.randn(8, 8), 4)
expect_value_error(mqa_projections, x, wq, wk, wv, 3)
