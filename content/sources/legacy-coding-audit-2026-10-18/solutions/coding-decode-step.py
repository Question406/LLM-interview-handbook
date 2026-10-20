import torch


def repeat_kv(x, n_rep):
    """[B, H_kv, S, D] -> [B, H_kv * n_rep, S, D]，每个 KV 头连续复制 n_rep 次。"""
    if n_rep == 1:
        return x
    batch, kv_heads, seq_len, head_dim = x.shape
    expanded = x[:, :, None].expand(batch, kv_heads, n_rep, seq_len, head_dim)
    return expanded.reshape(batch, kv_heads * n_rep, seq_len, head_dim)


def decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, n_rep):
    """一步 decode：追加 KV，GQA 注意力，输出投影和 lm_head。

    q: [B, H_q, 1, D]，k_t / v_t: [B, H_kv, 1, D]，都已做过 RoPE。
    cache_k / cache_v: [B, H_kv, S, D]。返回 logits [B, 1, V] 和长度 S + 1 的新 cache。
    """
    if q.size(1) != k_t.size(1) * n_rep:
        raise ValueError(f"H_q={q.size(1)} must equal H_kv={k_t.size(1)} * n_rep={n_rep}")
    cache_k = torch.cat([cache_k, k_t], dim=2)  # [B, H_kv, S + 1, D]
    cache_v = torch.cat([cache_v, v_t], dim=2)
    k = repeat_kv(cache_k, n_rep)               # [B, H_q, S + 1, D]
    v = repeat_kv(cache_v, n_rep)
    scale = q.size(-1) ** -0.5
    scores = torch.matmul(q, k.transpose(-2, -1)) * scale  # [B, H_q, 1, S + 1]
    probs = torch.softmax(scores.float(), dim=-1).to(q.dtype)
    heads = torch.matmul(probs, v)                         # [B, H_q, 1, D]
    hidden = heads.transpose(1, 2).reshape(q.size(0), 1, -1)  # [B, 1, H_q * D]
    hidden = hidden @ w_o.T
    logits = hidden @ w_head.T                              # [B, 1, V]
    return logits, cache_k, cache_v


def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


torch.set_num_threads(1)
torch.manual_seed(0)
q = torch.randn(2, 4, 1, 2)
k_t = torch.randn(2, 2, 1, 2)
v_t = torch.randn_like(k_t)
empty_k = torch.empty(2, 2, 0, 2)
empty_v = empty_k.clone()
w_o = torch.eye(8)
w_head = torch.randn(5, 8)

# 空 cache：注意力权重为 1，输出就是本步 v 经过 GQA repeat 后的投影
logits, cache_k, cache_v = decode_step(q, k_t, v_t, empty_k, empty_v, w_o, w_head, 2)
expected = v_t.repeat_interleave(2, 1).transpose(1, 2).reshape(2, 1, 8) @ w_head.T
assert logits.shape == (2, 1, 5)
assert cache_k.shape == (2, 2, 1, 2)
assert torch.allclose(logits, expected)

# 传入的 cache 不被修改，新 cache 只有 H_kv 个头
assert empty_k.shape[2] == 0
assert cache_k.shape[1] == 2

# 第二步：cache 长度加一，结果与手算的 softmax 注意力一致
logits, cache_k, cache_v = decode_step(q, k_t, v_t, cache_k, cache_v, w_o, w_head, 2)
assert cache_k.shape[2] == 2
k_full = cache_k.repeat_interleave(2, 1)
v_full = cache_v.repeat_interleave(2, 1)
probs = torch.softmax(q @ k_full.transpose(-2, -1) / 2 ** 0.5, dim=-1)
expected = (probs @ v_full).transpose(1, 2).reshape(2, 1, 8) @ w_head.T
assert torch.allclose(logits, expected, atol=1e-6)

# repeat_kv 与 repeat_interleave 语义相同；n_rep=1 原样返回
x = torch.randn(1, 3, 4, 2)
assert torch.equal(repeat_kv(x, 3), x.repeat_interleave(3, 1))
assert repeat_kv(x, 1) is x

# 头数对不上时报错
expect_error(ValueError, decode_step, q, k_t, v_t, empty_k, empty_v, w_o, w_head, 3)
