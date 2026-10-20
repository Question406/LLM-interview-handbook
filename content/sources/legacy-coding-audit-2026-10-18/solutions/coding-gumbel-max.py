import math

import torch


def gumbel_noise(shape, generator=None, device=None, dtype=torch.float32):
    """标准 Gumbel 噪声 -log(-log U)，U 截在当前 dtype 可表示的开区间 (0, 1) 内。"""
    uniform = torch.rand(shape, generator=generator, device=device, dtype=dtype)
    finfo = torch.finfo(dtype)
    uniform = uniform.clamp(min=finfo.tiny, max=1 - finfo.eps)
    return -torch.log(-torch.log(uniform))


def _check_inputs(logits, tau):
    if not math.isfinite(tau) or tau <= 0:
        raise ValueError(f"tau must be a finite positive number, got {tau}")
    if torch.isnan(logits).any() or torch.isposinf(logits).any():
        raise ValueError("logits must not contain NaN or +inf")
    if not torch.isfinite(logits).any(dim=-1).all():
        raise ValueError("every row needs at least one unmasked (finite) logit")


def gumbel_max(logits, tau=1.0, generator=None):
    """沿最后一维从 softmax(logits / tau) 抽一个类别下标。"""
    _check_inputs(logits, tau)
    noise = gumbel_noise(logits.shape, generator, logits.device, logits.dtype)
    return torch.argmax(logits / tau + noise, dim=-1)


def gumbel_softmax(logits, tau=1.0, hard=False, generator=None):
    """松弛输出 softmax((logits + g) / tau)；hard=True 时前向 one-hot、反向沿松弛。"""
    _check_inputs(logits, tau)
    noise = gumbel_noise(logits.shape, generator, logits.device, logits.dtype)
    soft = torch.softmax((logits + noise) / tau, dim=-1)
    if not hard:
        return soft
    index = soft.argmax(dim=-1, keepdim=True)
    one_hot = torch.zeros_like(soft).scatter_(-1, index, 1.0)
    return one_hot + soft - soft.detach()  # 前向值是 one_hot，梯度来自 soft


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# gumbel_max 的采样频率匹配 softmax(z / tau)
logits = torch.tensor([[0.0, 2.0]]).expand(30000, -1)
for tau in (0.5, 2.0):
    generator = torch.Generator().manual_seed(7)
    samples = gumbel_max(logits, tau, generator)
    expected = torch.softmax(torch.tensor([0.0, 2.0]) / tau, dim=-1)[1]
    assert abs(samples.float().mean() - expected) < 0.015

# 同一份噪声下，松弛温度不改变 hard 选出的类别；输出每行和为 1
z = torch.tensor([[0.1, 0.7, -0.2]], requires_grad=True)
sharp = gumbel_softmax(z, 0.3, True, torch.Generator().manual_seed(2))
smooth = gumbel_softmax(z, 3.0, True, torch.Generator().manual_seed(2))
assert sharp.argmax(-1).equal(smooth.argmax(-1))
assert torch.allclose(sharp.sum(-1), torch.ones(1))

# hard=True 的梯度来自松弛输出，是有限值
(sharp * torch.tensor([[1.0, 2.0, 3.0]])).sum().backward()
assert torch.isfinite(z.grad).all()

# 被 -inf mask 的类别永远不会被选中
masked = torch.tensor([[float("-inf"), 0.0, float("-inf")]]).expand(1000, -1)
assert (gumbel_max(masked, 1.0, torch.Generator().manual_seed(0)) == 1).all()

# 噪声没有 inf / NaN
assert torch.isfinite(gumbel_noise((10000,))).all()

# 非法温度、整行被 mask、NaN
expect_value_error(gumbel_max, torch.zeros(1, 2), 0.0)
expect_value_error(gumbel_max, torch.full((1, 2), float("-inf")), 1.0)
expect_value_error(gumbel_softmax, torch.tensor([[0.0, float("nan")]]), 1.0)
