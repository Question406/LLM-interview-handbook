import torch
import torch.nn.functional as F


def repeat_kv(x, n_rep):
    """[B, H_kv, S, D] -> [B, H_kv * n_rep, S, D]，相邻 n_rep 个 head 共用一个 KV head。"""
    if not isinstance(n_rep, int) or n_rep < 1:
        raise ValueError(f"n_rep must be a positive int, got {n_rep!r}")
    if n_rep == 1:
        return x
    B, H_kv, S, D = x.shape
    return (
        x[:, :, None, :, :]
        .expand(B, H_kv, n_rep, S, D)
        .reshape(B, H_kv * n_rep, S, D)
    )


def gqa_attn(q, k, v):
    """GQA 注意力（无 mask）。q: [B, H_q, T, D]；k, v: [B, H_kv, S, D]；返回 [B, H_q, T, D]。"""
    B, H_q, T, D = q.shape
    H_kv = k.shape[1]
    if k.shape != v.shape:
        raise ValueError(f"k and v shapes differ: {tuple(k.shape)} vs {tuple(v.shape)}")
    if k.shape[0] != B or k.shape[-1] != D:
        raise ValueError(f"k shape {tuple(k.shape)} does not match q shape {tuple(q.shape)}")
    if H_q % H_kv != 0:
        raise ValueError(f"H_q={H_q} is not a multiple of H_kv={H_kv}")

    n_rep = H_q // H_kv
    k_rep = repeat_kv(k, n_rep)  # [B, H_q, S, D]
    v_rep = repeat_kv(v, n_rep)
    scores = torch.matmul(q, k_rep.transpose(-2, -1)) * D ** -0.5  # [B, H_q, T, S]
    probs = torch.softmax(scores.float(), dim=-1).to(q.dtype)
    return torch.matmul(probs, v_rep)


torch.set_num_threads(1)
torch.manual_seed(0)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


# head 顺序是 [k0, k0, k1, k1]，不是交错的
kv = torch.arange(4.0).reshape(1, 2, 1, 2)
assert torch.equal(repeat_kv(kv, 2)[:, :, 0, 0], torch.tensor([[0.0, 0.0, 2.0, 2.0]]))

# n_rep = 1 原样返回（MHA）
assert repeat_kv(kv, 1) is kv

# 和 PyTorch SDPA + repeat_interleave 一致
q = torch.randn(2, 4, 3, 2)
k = torch.randn(2, 2, 5, 2)
v = torch.randn_like(k)
out = gqa_attn(q, k, v)
ref = F.scaled_dot_product_attention(q, k.repeat_interleave(2, 1), v.repeat_interleave(2, 1))
assert out.shape == (2, 4, 3, 2)
assert torch.allclose(out, ref, atol=1e-6)

# MQA 端点：H_kv = 1
k1 = torch.randn(2, 1, 5, 2)
v1 = torch.randn_like(k1)
ref1 = F.scaled_dot_product_attention(q, k1.expand(2, 4, 5, 2), v1.expand(2, 4, 5, 2))
assert torch.allclose(gqa_attn(q, k1, v1), ref1, atol=1e-6)

# 非法输入
expect_value_error(repeat_kv, kv, 0)
expect_value_error(gqa_attn, torch.randn(1, 3, 2, 2), torch.randn(1, 2, 2, 2), torch.randn(1, 2, 2, 2))
expect_value_error(gqa_attn, q, k, torch.randn(2, 2, 4, 2))
