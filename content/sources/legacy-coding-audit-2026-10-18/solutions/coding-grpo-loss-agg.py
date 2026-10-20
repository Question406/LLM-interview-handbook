import torch


def _check_shapes(per_tok, mask):
    if per_tok.ndim != 2 or per_tok.shape != mask.shape:
        raise ValueError("per_tok and mask must both be [B, T], got "
                         f"{tuple(per_tok.shape)} and {tuple(mask.shape)}")


def loss_seq_mean(per_tok, mask):
    """每条回答内对有效 token 取平均，再对 B 条回答平均；空回答贡献 0，仍计入 B。"""
    _check_shapes(per_tok, mask)
    lengths = mask.sum(dim=-1).clamp(min=1)          # [B]，空回答的分母取 1
    per_seq = (per_tok * mask).sum(dim=-1) / lengths  # [B]
    return per_seq.mean()


def loss_token_mean(per_tok, mask):
    """整个 batch 的有效 token 一起平均；没有有效 token 时返回 0。"""
    _check_shapes(per_tok, mask)
    return (per_tok * mask).sum() / mask.sum().clamp(min=1)


def loss_const_norm(per_tok, mask, max_len):
    """有效 token 的 loss 总和除以常数 B * max_len（Dr. GRPO）。"""
    _check_shapes(per_tok, mask)
    batch, seq_len = per_tok.shape
    if not isinstance(max_len, int) or max_len < seq_len:
        raise ValueError(f"max_len must be an int >= T={seq_len}, got {max_len!r}")
    return (per_tok * mask).sum() / (batch * max_len)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
per_tok = torch.tensor([[1.0, 3.0, 99.0], [2.0, 4.0, 6.0]], requires_grad=True)
mask = torch.tensor([[1.0, 1.0, 0.0], [1.0, 1.0, 1.0]])

# 三种聚合：seq = (2 + 4) / 2，token = 16 / 5，const = 16 / (2 * 4)；pad 上的 99 不参与
assert loss_seq_mean(per_tok, mask) == 3
assert torch.allclose(loss_token_mean(per_tok, mask), torch.tensor(3.2))
assert loss_const_norm(per_tok, mask, 4) == 2

# 梯度就是每个 token 的权重：seq-mean 是 1 / (B * |o_i|)，短回答的 token 权重更大
grad, = torch.autograd.grad(loss_seq_mean(per_tok, mask), per_tok)
assert torch.allclose(grad, torch.tensor([[0.25, 0.25, 0.0], [1 / 6, 1 / 6, 1 / 6]]))

# token-mean 和常数归一下，每个有效 token 权重相同，pad 权重为 0
grad, = torch.autograd.grad(loss_token_mean(per_tok, mask), per_tok)
assert torch.allclose(grad, mask / 5)
grad, = torch.autograd.grad(loss_const_norm(per_tok, mask, 4), per_tok)
assert torch.allclose(grad, mask / 8)

# 全部被 mask：返回 0，梯度也全是 0，不出现 NaN
all_masked = torch.zeros_like(mask)
zero = loss_token_mean(per_tok, all_masked)
assert zero == 0
assert torch.all(torch.autograd.grad(zero, per_tok)[0] == 0)
assert loss_seq_mean(per_tok, all_masked) == 0

# 空回答在 seq-mean 里贡献 0 但仍计入 B：只剩第二条回答的平均 4，再除以 2
one_empty = torch.tensor([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
assert loss_seq_mean(per_tok, one_empty) == 2

# 非法输入：max_len 小于 T，或 per_tok 和 mask 形状不一致
expect_value_error(loss_const_norm, per_tok, mask, 2)
expect_value_error(loss_token_mean, per_tok, mask[:, :2])
