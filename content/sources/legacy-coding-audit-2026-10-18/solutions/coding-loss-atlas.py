import torch
import torch.nn.functional as F


def surrogate(logp, w, mask, denom):
    """梯度等价的替身 loss：-sum(sg(w) * logp * mask) / denom。

    logp: [B, T]，需要梯度；w: [B, T] 或 [B, 1]；denom 要和原 loss 的归约方式一致，且 > 0。
    替身的数值不等于原 loss，只有对 logp 的梯度相同。
    """
    if denom <= 0:
        raise ValueError(f"denom must be positive, got {denom}")
    return -(w.detach() * logp * mask).sum() / denom


def w_k3(logp, ref_logp, beta):
    """k3 KL 放进 loss 时每个采样 token 的权重 beta * (rho - 1)，rho = pi_ref / pi。[B, T]。"""
    rho = torch.exp(ref_logp - logp).detach()
    return beta * (rho - 1)


def w_pairwise(lw, ll, beta, ref_margin=0.0, len_w=1.0, len_l=1.0, gamma=0.0):
    """DPO / SimPO 每个 token 的权重，返回 (chosen 权重, rejected 权重)，形状 [B]。

    lw, ll: [B]，chosen / rejected 的序列 logprob（token 求和）。
    DPO：len_w = len_l = 1，ref_margin = ref_w - ref_l，gamma = 0。
    SimPO：ref_margin = 0，len_* = 回答长度 |y|，gamma > 0。
    """
    z = beta * (lw / len_w - ll / len_l - ref_margin) - gamma
    coefficient = (beta * torch.sigmoid(-z)).detach()
    return coefficient / len_w, -coefficient / len_l


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def pairwise_case(beta, **kwargs):
    """比较 -logsigmoid(z) 的真实梯度和替身梯度。"""
    chosen = torch.randn(2, 3, requires_grad=True)
    rejected = torch.randn(2, 3, requires_grad=True)
    sum_w = chosen.sum(-1)
    sum_l = rejected.sum(-1)
    z = beta * (sum_w / kwargs.get("len_w", 1) - sum_l / kwargs.get("len_l", 1)
                - kwargs.get("ref_margin", 0)) - kwargs.get("gamma", 0)
    true_grads = torch.autograd.grad(-F.logsigmoid(z).mean(), (chosen, rejected))
    weight_w, weight_l = w_pairwise(sum_w, sum_l, beta, **kwargs)
    full_mask = torch.ones(2, 3)
    sur = surrogate(chosen, weight_w[:, None], full_mask, 2) + surrogate(rejected, weight_l[:, None], full_mask, 2)
    sur_grads = torch.autograd.grad(sur, (chosen, rejected))
    for expected, actual in zip(true_grads, sur_grads):
        assert torch.allclose(expected, actual, atol=1e-6)


torch.set_num_threads(1)
torch.manual_seed(0)
logp = torch.randn(2, 3, requires_grad=True)
ref = torch.randn(2, 3)
mask = torch.ones(2, 3)

# k3 KL：真实 loss 的梯度 == 替身的梯度
rho = (ref - logp).exp()
k3_loss = ((rho - (ref - logp) - 1) * mask).mean() * 0.1
(grad_true,) = torch.autograd.grad(k3_loss, logp)
(grad_sur,) = torch.autograd.grad(surrogate(logp, w_k3(logp, ref, 0.1), mask, mask.sum()), logp)
assert torch.allclose(grad_true, grad_sur, atol=1e-6)

# k3：logp == ref 时权重和梯度都是 0
assert torch.allclose(w_k3(logp, logp.detach(), 0.1), torch.zeros(2, 3))

# DPO（带参考模型的 margin）和 SimPO（长度归一 + gamma）的梯度都对得上
pairwise_case(0.1, ref_margin=torch.tensor([0.1, -0.2]))
pairwise_case(0.1, len_w=torch.tensor([2.0, 3.0]), len_l=torch.tensor([3.0, 2.0]), gamma=0.5)

# DPO margin z = 0：chosen 权重 beta/2，rejected 权重 -beta/2
weight_w, weight_l = w_pairwise(torch.tensor([0.0]), torch.tensor([0.0]), 0.2)
assert torch.allclose(weight_w, torch.tensor([0.1]))
assert torch.allclose(weight_l, torch.tensor([-0.1]))

# mask 外的 token 没有梯度
half_mask = torch.tensor([[1.0, 1.0, 0.0], [1.0, 0.0, 0.0]])
(grad_masked,) = torch.autograd.grad(surrogate(logp, torch.ones(2, 3), half_mask, half_mask.sum()), logp)
assert torch.all(grad_masked[half_mask == 0] == 0)

# 分母必须为正
expect_value_error(surrogate, logp, torch.ones(2, 3), mask, 0)
