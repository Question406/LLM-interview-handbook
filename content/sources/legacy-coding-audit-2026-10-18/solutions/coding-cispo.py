import math

import torch


def cispo_loss(policy_logprobs, old_logprobs, advantages, mask, eps_low=1.0, eps_high=0.28):
    """CISPO 损失：对有效 token 取平均。

    policy_logprobs, old_logprobs, mask: [B, T]；advantages 可广播到 [B, T]。
    IS 权重 r 截断到 [1 - eps_low, 1 + eps_high] 后 detach，只作为 logprob 前的常数系数。
    mask 全为 0 时返回 0（仍可反传，梯度为 0）。
    """
    ratio = torch.exp(policy_logprobs - old_logprobs).detach()
    weight = ratio.clamp(1 - eps_low, 1 + eps_high)
    per_token = -weight * advantages * policy_logprobs
    return (per_token * mask).sum() / mask.sum().clamp(min=1)


def ppo_weight(ratio, adv, eps=0.2):
    """PPO clip 目标写成加权 logprob 时的权重 sg(r * A * active)；出界 token 权重为 0。"""
    active = torch.where(adv >= 0, ratio <= 1 + eps, ratio >= 1 - eps)
    return (ratio * adv * active).detach()


def cispo_weight(ratio, adv, eps_low=1.0, eps_high=0.28):
    """CISPO 的权重 sg(clip(r)) * A；出界 token 仍有权重，只是被截到边界。"""
    return (ratio.clamp(1 - eps_low, 1 + eps_high) * adv).detach()


torch.set_num_threads(1)

# ratio = 2 超出上界：CISPO 的梯度系数被截到 1.28，仍不为 0
logprobs = torch.tensor([[math.log(2.0)]], requires_grad=True)
old = torch.zeros_like(logprobs)
adv = torch.ones_like(logprobs)
mask = torch.ones_like(logprobs)
loss = cispo_loss(logprobs, old, adv, mask)
(grad,) = torch.autograd.grad(loss, logprobs)
assert torch.allclose(grad, torch.tensor([[-1.28]]))

# 同一个 token，PPO 权重为 0，CISPO 权重为 1.28
ratio = torch.tensor([[2.0]])
assert ppo_weight(ratio, adv).item() == 0
assert torch.allclose(cispo_weight(ratio, adv), torch.tensor([[1.28]]))

# 界内两者相同，都是 r * A
inside = torch.tensor([1.1])
assert torch.allclose(ppo_weight(inside, torch.tensor([2.0])), torch.tensor([2.2]))
assert torch.allclose(cispo_weight(inside, torch.tensor([2.0])), torch.tensor([2.2]))

# A < 0 且 r < 1 - eps：PPO 置零；eps_low = 1 时 CISPO 不设下界，权重是 r * A
low_ratio = torch.tensor([0.5])
negative = torch.tensor([-1.0])
assert ppo_weight(low_ratio, negative).item() == 0
assert torch.allclose(cispo_weight(low_ratio, negative), torch.tensor([-0.5]))

# mask 只取一部分 token：分母是有效 token 数
two_logprobs = torch.tensor([[-1.0, -3.0]], requires_grad=True)
partial = cispo_loss(two_logprobs, two_logprobs.detach(), torch.ones(1, 2), torch.tensor([[1.0, 0.0]]))
assert torch.allclose(partial, torch.tensor(1.0))

# 空 mask：返回 0，且可以反传、梯度为 0
empty = cispo_loss(logprobs, old, adv, torch.zeros_like(mask))
assert empty == 0
assert torch.all(torch.autograd.grad(empty, logprobs)[0] == 0)
