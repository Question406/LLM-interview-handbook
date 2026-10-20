import math

import torch


def dropout(x, p, training, generator=None):
    """Inverted dropout：训练时以 1-p 保留并除以 1-p，推理原样返回。要求 0 <= p < 1。"""
    if not math.isfinite(p) or p < 0.0 or p >= 1.0:
        raise ValueError(f"p must be in [0, 1), got {p}")
    if not training or p == 0.0:
        return x
    keep = 1.0 - p
    mask = torch.empty_like(x).bernoulli_(keep, generator=generator)
    return x * mask / keep


def attn_with_dropout(scores, p, training, generator=None):
    """scores: [B, H, T, S]，已用 -inf 加过 mask。dropout 打在 softmax 之后的权重上。"""
    weights = torch.softmax(scores, dim=-1)
    return dropout(weights, p, training, generator)


torch.set_num_threads(1)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


x = torch.ones(100000)

# 同一种子结果可复现，期望约等于 1
first = dropout(x, 0.3, True, torch.Generator().manual_seed(8))
second = dropout(x, 0.3, True, torch.Generator().manual_seed(8))
assert torch.equal(first, second)
assert abs(first.mean().item() - 1) < 0.015

# p = 0.5 时训练输出只有 0 和 2
halves = dropout(x, 0.5, True, torch.Generator().manual_seed(0))
assert set(halves.unique().tolist()) == {0.0, 2.0}

# 推理或 p = 0：原样返回
assert torch.equal(dropout(x, 0.3, False), x)
assert torch.equal(dropout(x, 0.0, True), x)

# 非法 p：推理时也报错
expect_value_error(lambda: dropout(x, 1.0, False))
expect_value_error(lambda: dropout(x, 1.0, True))
expect_value_error(lambda: dropout(x, -0.1, True))
expect_value_error(lambda: dropout(x, float("nan"), False))

# attention dropout：推理时每行和为 1；训练时非零权重被放大 1/(1-p)，行和不再固定为 1
scores = torch.randn(2, 3, 4, 5, generator=torch.Generator().manual_seed(1))
scores[..., -1] = float("-inf")
eval_weights = attn_with_dropout(scores, 0.5, False)
assert torch.allclose(eval_weights.sum(-1), torch.ones(2, 3, 4))
assert torch.all(eval_weights[..., -1] == 0)
train_weights = attn_with_dropout(scores, 0.5, True, torch.Generator().manual_seed(2))
kept = train_weights != 0
assert torch.allclose(train_weights[kept], 2 * eval_weights[kept])
