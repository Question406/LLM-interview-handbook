import math

import torch


def _check_eps(eps_low, eps_high):
    if eps_low < 0 or eps_high < 0:
        raise ValueError(f"clip ranges must be non-negative, got eps_low={eps_low}, eps_high={eps_high}")


def sequence_log_ratio(policy_logprobs, old_logprobs, mask):
    """log s_i：每条序列有效 token 上 log ratio 的平均。[B, T] -> [B]。"""
    lengths = mask.sum(-1).clamp(min=1)
    return ((policy_logprobs - old_logprobs) * mask).sum(-1) / lengths


def gspo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4):
    """GSPO 的 clipped 目标（取负作为 loss）。

    *_logprobs, mask: [B, T]；advantages: [B]，视为常量。
    序列 ratio s_i 是 token ratio 的几何平均，clip 在序列上做。
    """
    _check_eps(eps_low, eps_high)
    s = torch.exp(sequence_log_ratio(policy_logprobs, old_logprobs, mask))   # [B]
    clipped = s.clamp(1 - eps_low, 1 + eps_high)
    objective = torch.minimum(s * advantages, clipped * advantages)
    return -objective.mean()


def gspo_loss_sft_style(policy_logprobs, old_logprobs, advantages, mask, eps_low=3e-4, eps_high=4e-4):
    """和 gspo_loss 梯度相同的加权 logprob 写法。

    每条序列的 token 共用权重 sg(s_i * A_i * active_i) / |y_i|。
    """
    _check_eps(eps_low, eps_high)
    lengths = mask.sum(-1).clamp(min=1)                                        # [B]
    s = torch.exp(sequence_log_ratio(policy_logprobs, old_logprobs, mask)).detach()
    active = torch.where(advantages >= 0, s <= 1 + eps_high, s >= 1 - eps_low)
    weight = (s * advantages * active / lengths).detach()                      # [B]
    return -(weight[:, None] * policy_logprobs * mask).sum() / advantages.shape[0]


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def grad_of(loss_fn, logprobs, *args):
    (grad,) = torch.autograd.grad(loss_fn(logprobs, *args), logprobs)
    return grad


torch.set_num_threads(1)
torch.manual_seed(2)

# 两种写法对 policy_logprobs 的梯度一致；mask 外的 token 梯度为 0
logprobs = torch.randn(3, 5, requires_grad=True)
old = logprobs.detach() + 0.0001 * torch.randn(3, 5)
adv = torch.tensor([1.0, -1.0, 2.0])
mask = torch.tensor([[1, 1, 0, 0, 0], [1, 1, 1, 1, 1], [1, 0, 0, 0, 0.0]])
grad_clipped = grad_of(gspo_loss, logprobs, old, adv, mask)
grad_weighted = grad_of(gspo_loss_sft_style, logprobs, old, adv, mask)
assert torch.allclose(grad_clipped, grad_weighted, atol=1e-6)
assert torch.all(grad_clipped[mask == 0] == 0)

# token ratio 为 [4, 1/4]：几何平均 s = 1，loss = -1；算术平均会得到 2.125
pair = torch.tensor([[math.log(4.0), math.log(0.25)]], requires_grad=True)
loss = gspo_loss(pair, torch.zeros_like(pair), torch.ones(1), torch.ones_like(pair))
assert torch.allclose(loss, torch.tensor(-1.0))

# A > 0 且 s 超出上界：整条序列被 clip，两种写法梯度都为 0
far = torch.zeros(1, 3, requires_grad=True)
far_old = torch.full((1, 3), -0.01)
assert torch.all(grad_of(gspo_loss, far, far_old, torch.ones(1), torch.ones(1, 3)) == 0)
assert torch.all(grad_of(gspo_loss_sft_style, far, far_old, torch.ones(1), torch.ones(1, 3)) == 0)

# 负的 clip 范围报错
expect_value_error(gspo_loss, logprobs, old, adv, mask, eps_low=-1e-4)
