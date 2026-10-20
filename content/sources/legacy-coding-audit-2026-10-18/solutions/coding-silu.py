import torch
import torch.nn.functional as F


def sigmoid_stable(x):
    """数值稳定的 sigmoid：只计算 exp(-|x|)，任何有限输入都不溢出。返回 float32。"""
    x = x.float()
    z = torch.exp(-torch.abs(x))  # z ∈ (0, 1]
    return torch.where(x < 0, z / (1 + z), 1 / (1 + z))


def silu(x):
    """SiLU(x) = x * sigmoid(x)，在 float32 里计算，输出转回输入 dtype。"""
    return (x.float() * sigmoid_stable(x)).to(x.dtype)


def silu_tanh(x):
    """用 sigmoid(x) = (1 + tanh(x / 2)) / 2 计算 SiLU，作为独立对照。"""
    x32 = x.float()
    return (x32 * (0.5 * (1.0 + torch.tanh(0.5 * x32)))).to(x.dtype)


torch.set_num_threads(1)

x = torch.tensor([-1000.0, -40.0, -2.0, 0.0, 2.0, 40.0, 1000.0], requires_grad=True)

# 前向：极端值也有限，和 F.silu 一致
ours = silu(x)
reference = F.silu(x)
assert torch.isfinite(ours).all()
assert torch.allclose(ours, reference, atol=1e-6)

# 反向：梯度和 F.silu 一致，没有 NaN
grad_ours, = torch.autograd.grad(ours.sum(), x)
grad_reference, = torch.autograd.grad(reference.sum(), x)
assert torch.isfinite(grad_ours).all()
assert torch.allclose(grad_ours, grad_reference, atol=1e-6)

# tanh 形式作为独立对照
assert torch.allclose(silu_tanh(x), reference, atol=1e-5)

# 题面示例
assert silu(torch.tensor(0.0)).item() == 0
assert abs(silu(torch.tensor(1000.0)).item() - 1000) < 1e-3
assert abs(silu(torch.tensor(-1000.0)).item()) < 1e-6

# sigmoid_stable 在两侧都不溢出，且 sigma(-x) = 1 - sigma(x)
grid = torch.linspace(-50, 50, 101)
assert torch.isfinite(sigmoid_stable(grid)).all()
assert torch.allclose(sigmoid_stable(-grid), 1 - sigmoid_stable(grid), atol=1e-6)

# 半精度输入：输出 dtype 不变，-20 处结果约为 0 而不是 NaN
half = torch.tensor([-20.0, 0.0, 3.0], dtype=torch.float16)
assert silu(half).dtype == torch.float16
assert torch.allclose(silu(half).float(), F.silu(half.float()), atol=1e-2)
assert torch.isfinite(silu(half)).all()

# 输出形状不变
assert silu(torch.randn(2, 3, 4)).shape == (2, 3, 4)
