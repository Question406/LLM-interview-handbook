import math

import torch
from torch import nn


def total_grad_norm(params):
    """所有非 None 梯度的全局 L2 范数；有 NaN/Inf 时返回 inf。"""
    total = 0.0
    for param in params:
        if param.grad is None:
            continue
        grad = param.grad.detach().float()  # 低精度梯度先转 float32，平方和不溢出
        if not torch.isfinite(grad).all():
            return float("inf")
        total += float(grad.norm(2).item() ** 2)
    return math.sqrt(total)


def clip_grad_norm_(params, max_norm, eps=1e-6, error_if_nonfinite=True):
    """按全局 L2 范数原位裁剪梯度，返回裁剪前的范数。

    范数非有限时：默认抛 RuntimeError；error_if_nonfinite=False 时返回 inf。两种情况都不改梯度。
    """
    if not (math.isfinite(max_norm) and max_norm >= 0):
        raise ValueError(f"max_norm must be finite and non-negative, got {max_norm}")
    params = [param for param in params if param.grad is not None]
    norm = total_grad_norm(params)
    if not math.isfinite(norm):
        if error_if_nonfinite:
            raise RuntimeError("gradient norm is non-finite, no gradients were modified")
        return norm
    scale = max_norm / (norm + eps)
    if scale < 1.0:
        for param in params:
            param.grad.mul_(scale)
    return norm


torch.set_num_threads(1)


def expect_error(error_type, action):
    try:
        action()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


# 题面示例：范数 5 裁到 2.5，返回裁剪前的范数
param = nn.Parameter(torch.zeros(2))
param.grad = torch.tensor([3.0, 4.0])
norm = clip_grad_norm_([param], 2.5)
assert norm == 5
assert torch.allclose(param.grad, torch.tensor([1.5, 2.0]), atol=1e-6)

# 范数没超过阈值：梯度不变
param.grad = torch.tensor([3.0, 4.0])
assert clip_grad_norm_([param], 10.0) == 5
assert torch.equal(param.grad, torch.tensor([3.0, 4.0]))

# 含 NaN：默认报错，梯度保持原状
param.grad = torch.tensor([float("nan"), 1.0])
before = param.grad.clone()
expect_error(RuntimeError, lambda: clip_grad_norm_([param], 1))
assert torch.allclose(param.grad, before, equal_nan=True)

# 后一个参数含 Inf 时，前一个参数的梯度也不能被先改掉
first = nn.Parameter(torch.zeros(2))
first.grad = torch.tensor([30.0, 40.0])
second = nn.Parameter(torch.zeros(1))
second.grad = torch.tensor([float("inf")])
assert clip_grad_norm_([first, second], 1.0, error_if_nonfinite=False) == float("inf")
assert torch.equal(first.grad, torch.tensor([30.0, 40.0]))

# 没有梯度的参数被跳过；全都没有梯度时范数为 0
assert total_grad_norm([nn.Parameter(torch.ones(2))]) == 0
no_grad_params = [nn.Parameter(torch.zeros(1)), nn.Parameter(torch.ones(3))]
assert clip_grad_norm_(no_grad_params, 1.0) == 0

# 多个参数按全局范数统一缩放，方向不变
left = nn.Parameter(torch.zeros(1))
left.grad = torch.tensor([6.0])
right = nn.Parameter(torch.zeros(1))
right.grad = torch.tensor([8.0])
assert clip_grad_norm_(iter([left, right]), 5.0) == 10
assert torch.allclose(left.grad, torch.tensor([3.0]), atol=1e-5)
assert torch.allclose(right.grad, torch.tensor([4.0]), atol=1e-5)

# fp16 梯度的平方和超出 fp16 范围，也能算对
half = nn.Parameter(torch.zeros(2, dtype=torch.float16))
half.grad = torch.tensor([300.0, 400.0], dtype=torch.float16)
assert total_grad_norm([half]) == 500

# 非法 max_norm
expect_error(ValueError, lambda: clip_grad_norm_([left], -1.0))
expect_error(ValueError, lambda: clip_grad_norm_([left], float("inf")))
