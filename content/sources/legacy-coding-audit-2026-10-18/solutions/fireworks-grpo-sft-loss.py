import math

import torch


def sft_loss(weights, logprobs):
    """加权负对数似然，按 token 数平均；权重可正可负，不按权重和归一化。"""
    return -(weights.detach() * logprobs).mean()


def compute_grpo_loss_per_rollout(policy_logprobs, sampling_logprobs, advantages, clip_eps=0.2):
    """标准 clipped GRPO 目标的负值，按 token 平均。所有输入形状 [N]。"""
    ratio = torch.exp(policy_logprobs - sampling_logprobs)
    clipped_ratio = ratio.clamp(1 - clip_eps, 1 + clip_eps)
    objective = torch.minimum(ratio * advantages, clipped_ratio * advantages)
    return -objective.mean()


def compute_grpo_loss_per_rollout_with_sft_loss(policy_logprobs, sampling_logprobs, advantages, epsilon=0.2):
    """复用 sft_loss 的等价写法：对 policy_logprobs 的梯度与上面的 clipped 目标相同。"""
    ratio = torch.exp(policy_logprobs - sampling_logprobs).detach()
    # 只挡住「朝有利方向走得太远」的那一侧
    active = torch.where(
        advantages >= 0,
        ratio <= 1 + epsilon,
        ratio >= 1 - epsilon,
    )
    weights = ratio * advantages * active
    return sft_loss(weights, policy_logprobs)


# 两个被 clip 的 token（ratio 1.5 且 A>0、ratio 0.5 且 A<0）梯度为 0，两版梯度一致
logprobs = torch.tensor([math.log(1.5), math.log(0.5), 0.1, -0.1], requires_grad=True)
old = torch.zeros(4)
adv = torch.tensor([1.0, -1.0, 1.0, -1.0])
(direct_grad,) = torch.autograd.grad(compute_grpo_loss_per_rollout(logprobs, old, adv), logprobs)
(sft_grad,) = torch.autograd.grad(compute_grpo_loss_per_rollout_with_sft_loss(logprobs, old, adv), logprobs)
assert torch.allclose(direct_grad, sft_grad)
assert direct_grad[0] == 0
assert direct_grad[1] == 0

# 反方向越界不 clip：ratio 1.5 但 A<0、ratio 0.5 但 A>0 仍有梯度
logprobs = torch.tensor([math.log(1.5), math.log(0.5)], requires_grad=True)
adv = torch.tensor([-1.0, 1.0])
(sft_grad,) = torch.autograd.grad(compute_grpo_loss_per_rollout_with_sft_loss(logprobs, torch.zeros(2), adv), logprobs)
assert torch.all(sft_grad != 0)

# 随机输入下两版梯度一致（边界上的不可微点概率为 0）
torch.manual_seed(0)
logprobs = torch.randn(8, requires_grad=True)
old = logprobs.detach() + 0.3 * torch.randn(8)
adv = torch.randn(8)
(direct_grad,) = torch.autograd.grad(compute_grpo_loss_per_rollout(logprobs, old, adv), logprobs)
(sft_grad,) = torch.autograd.grad(compute_grpo_loss_per_rollout_with_sft_loss(logprobs, old, adv), logprobs)
assert torch.allclose(direct_grad, sft_grad)

# 两版的 loss 数值不同，只有梯度相同
assert not torch.isclose(
    compute_grpo_loss_per_rollout(logprobs, old, adv),
    compute_grpo_loss_per_rollout_with_sft_loss(logprobs, old, adv),
)

# 权重正负抵消时也是有限值，梯度是 -w / N
values = torch.tensor([1.0, 2.0], requires_grad=True)
loss = sft_loss(torch.tensor([1.0, -1.0]), values)
assert torch.isfinite(loss)
assert torch.allclose(torch.autograd.grad(loss, values)[0], torch.tensor([-0.5, 0.5]))
