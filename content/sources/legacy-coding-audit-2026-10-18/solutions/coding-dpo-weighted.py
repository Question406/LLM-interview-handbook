import torch
import torch.nn.functional as F


def seq_logprob(tok_logp, mask):
    """[B, T] token logprob 按 mask 求和，得到 [B] 序列 logprob。"""
    return (tok_logp * mask).sum(-1)


def _dpo_margin(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta):
    """z = beta * ((logπ_w - logref_w) - (logπ_l - logref_l))，形状 [B]。"""
    if beta <= 0:
        raise ValueError(f"beta must be positive, got {beta}")
    chosen = seq_logprob(pol_w, mask_w) - seq_logprob(ref_w, mask_w)
    rejected = seq_logprob(pol_l, mask_l) - seq_logprob(ref_l, mask_l)
    return beta * (chosen - rejected)


def dpo_loss(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    """标准 DPO loss：-log sigmoid(z) 的 batch 平均。"""
    z = _dpo_margin(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta)
    return -F.logsigmoid(z).mean()


def dpo_loss_weighted(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta=0.1):
    """加权 logprob surrogate：数值不同于 DPO loss，但对 policy 的梯度相同。"""
    with torch.no_grad():
        z = _dpo_margin(pol_w, pol_l, ref_w, ref_l, mask_w, mask_l, beta)
        weight = beta * torch.sigmoid(-z)  # [B]，排反时接近 beta，排对时趋于 0
    batch_size = pol_w.shape[0]
    margin = seq_logprob(pol_w, mask_w) - seq_logprob(pol_l, mask_l)
    return -(weight * margin).sum() / batch_size


import math

torch.set_num_threads(1)
torch.manual_seed(4)

pol_w = torch.randn(3, 4, requires_grad=True)
pol_l = torch.randn(3, 4, requires_grad=True)
ref_w = torch.randn(3, 4)
ref_l = torch.randn(3, 4)
mask_w = torch.tensor([[1, 1, 0, 0], [1, 1, 1, 1], [1, 0, 0, 0.0]])
mask_l = torch.ones_like(mask_w)
args = (pol_w, pol_l, ref_w, ref_l, mask_w, mask_l)

# 两种写法对 policy 的梯度一致
grads_dpo = torch.autograd.grad(dpo_loss(*args), (pol_w, pol_l))
grads_weighted = torch.autograd.grad(dpo_loss_weighted(*args), (pol_w, pol_l))
for expected, actual in zip(grads_dpo, grads_weighted):
    assert torch.allclose(expected, actual, atol=1e-6)

# 被 mask 掉的 token 没有梯度
assert torch.all(grads_dpo[0][mask_w == 0] == 0)

# z = 0 时 loss = ln 2；chosen 相对更好时 loss < ln 2
zeros = torch.zeros(2, 3)
ones = torch.ones(2, 3)
assert math.isclose(dpo_loss(zeros, zeros, zeros, zeros, ones, ones).item(), math.log(2), rel_tol=1e-6)
assert dpo_loss(ones, zeros, zeros, zeros, ones, ones).item() < math.log(2)

# z 极负时 logsigmoid 仍然有限
assert torch.isfinite(dpo_loss(zeros, ones * 1e4, zeros, zeros, ones, ones, beta=1.0))

# beta 必须为正
try:
    dpo_loss(*args, beta=0.0)
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError for beta = 0")
