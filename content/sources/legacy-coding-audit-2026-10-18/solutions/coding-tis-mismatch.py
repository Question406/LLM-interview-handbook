import torch


def ppo_loss_tis(policy_logprobs, old_logprobs, rollout_logprobs, advantages, mask,
                 eps=0.2, C=2.0):
    """PPO clip loss 加截断重要性权重 min(π_old / μ, C)。所有输入 [B, T]，返回有效 token 平均。"""
    # old_logprobs 由训练端在 θ_old 上重算；rollout_logprobs 来自推理引擎
    ratio = torch.exp(policy_logprobs - old_logprobs)
    clipped = ratio.clamp(1 - eps, 1 + eps)
    objective = torch.minimum(ratio * advantages, clipped * advantages)
    weight = torch.exp(old_logprobs - rollout_logprobs).clamp(max=C).detach()
    return -(weight * objective * mask).sum() / mask.sum().clamp(min=1)


torch.set_num_threads(1)

policy = torch.tensor([[0.1, 0.2]], requires_grad=True)
old = torch.zeros_like(policy)
rollout = torch.tensor([[-1.0, 0.0]])
advantages = torch.tensor([[1.0, -1.0]])
mask = torch.ones_like(policy)

# 和按公式手写的参考值一致，梯度也一致
loss = ppo_loss_tis(policy, old, rollout, advantages, mask)
ratio = (policy - old).exp()
weight = (old - rollout).exp().clamp(max=2.0)
reference = -(weight * torch.minimum(ratio * advantages, ratio.clamp(0.8, 1.2) * advantages)).mean()
assert torch.allclose(loss, reference)
grad_loss, = torch.autograd.grad(loss, policy)
grad_ref, = torch.autograd.grad(reference, policy)
assert torch.allclose(grad_loss, grad_ref)

# old == rollout 时权重为 1，等于普通 PPO
plain = ppo_loss_tis(policy, old, old, advantages, mask)
plain_ref = -torch.minimum(ratio * advantages, ratio.clamp(0.8, 1.2) * advantages).mean()
assert torch.allclose(plain, plain_ref)

# 权重被截断到 C
far = torch.tensor([[-5.0, -5.0]])
capped = ppo_loss_tis(old, old, far, torch.ones(1, 2), mask, C=2.0)
assert torch.allclose(capped, torch.tensor(-2.0))

# 空 mask 返回 0
assert ppo_loss_tis(policy, old, rollout, advantages, torch.zeros_like(mask)) == 0
