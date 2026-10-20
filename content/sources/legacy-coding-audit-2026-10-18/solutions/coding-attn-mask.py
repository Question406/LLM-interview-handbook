import torch


def compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k):
    """合成因果 + padding + 文档边界的加性 attention bias。

    q_pos: [T]，k_pos: [S]，key_valid: [B, S]（True = 非 pad），
    doc_q: [B, T]，doc_k: [B, S]。返回 [B, 1, T, S]，保留位为 0，其余为 -inf。
    """
    causal = k_pos[None, :] <= q_pos[:, None]                      # [T, S]
    not_pad = key_valid[:, None, None, :]                          # [B, 1, 1, S]
    same_doc = doc_q[:, None, :, None] == doc_k[:, None, None, :]  # [B, 1, T, S]
    keep = causal[None, None] & not_pad & same_doc                 # [B, 1, T, S]
    bias = torch.zeros(keep.shape)
    return bias.masked_fill(~keep, float("-inf"))


def decode_attn_bias(s_len, key_valid, doc_ids):
    """单步 decode 的 bias：新 query 位于第 s_len - 1 列。

    key_valid、doc_ids: [B, s_len]。返回 [B, 1, 1, s_len]。
    """
    if s_len < 1:
        raise ValueError(f"s_len must be >= 1, got {s_len}")
    q_pos = torch.tensor([s_len - 1])
    k_pos = torch.arange(s_len)
    doc_q = doc_ids[:, s_len - 1:s_len]  # [B, 1]
    return compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_ids)


def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


torch.set_num_threads(1)

# 三个条件一起生效：pad、未来、跨文档都被屏蔽
q_pos = torch.tensor([1, 2])
k_pos = torch.arange(4)
key_valid = torch.tensor([[True, True, False, True]])
doc_q = torch.tensor([[0, 1]])
doc_k = torch.tensor([[0, 0, 1, 1]])
bias = compose_attn_bias(q_pos, k_pos, key_valid, doc_q, doc_k)
expected_keep = torch.tensor([[1, 1, 0, 0], [0, 0, 0, 0]], dtype=torch.bool)
assert bias.shape == (1, 1, 2, 4)
assert torch.equal(torch.isfinite(bias[0, 0]), expected_keep)
assert torch.all(bias[0, 0][expected_keep] == 0)

# 单文档、无 pad 时退化成普通因果下三角
positions = torch.arange(3)
all_valid = torch.ones(1, 3, dtype=torch.bool)
one_doc = torch.zeros(1, 3, dtype=torch.long)
bias = compose_attn_bias(positions, positions, all_valid, one_doc, one_doc)
assert torch.equal(torch.isfinite(bias[0, 0]), torch.ones(3, 3, dtype=torch.bool).tril())

# decode：新 token 能看到同文档的全部历史
bias = decode_attn_bias(3, all_valid, one_doc)
assert bias.shape == (1, 1, 1, 3)
assert torch.isfinite(bias).all()

# decode：新 token 在第二篇文档时看不到第一篇
bias = decode_attn_bias(3, all_valid, torch.tensor([[0, 1, 1]]))
assert torch.equal(torch.isfinite(bias[0, 0, 0]), torch.tensor([False, True, True]))

# s_len 必须至少为 1
expect_error(ValueError, decode_attn_bias, 0, all_valid, one_doc)
