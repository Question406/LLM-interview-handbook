import torch
import torch.nn.functional as F
from torch import nn


class LayerNorm(nn.Module):
    """沿最后一维做 LayerNorm：总体方差，float32 计算，输出转回输入 dtype。"""

    def __init__(self, dim, eps=1e-5):
        super().__init__()
        if dim < 1:
            raise ValueError(f"dim must be >= 1, got {dim}")
        if not eps > 0:
            raise ValueError(f"eps must be positive, got {eps}")
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(dim))
        self.beta = nn.Parameter(torch.zeros(dim))

    def forward(self, x):
        # x: [..., D]，例如 [B, T, D]；只在最后一维 D 上归约
        x32 = x.float()
        mean = x32.mean(dim=-1, keepdim=True)
        var = x32.var(dim=-1, keepdim=True, unbiased=False)  # 总体方差，除以 D
        normalized = (x32 - mean) * torch.rsqrt(var + self.eps)
        return (self.gamma * normalized + self.beta).to(x.dtype)


torch.set_num_threads(1)


def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


# 前向与 F.layer_norm 一致
layer = LayerNorm(4)
x = torch.randn(2, 3, 4, requires_grad=True)
output = layer(x)
reference = F.layer_norm(x, (4,), layer.gamma, layer.beta, layer.eps)
assert torch.allclose(output, reference, atol=1e-6)

# 对输入的梯度也一致
grad_ours, = torch.autograd.grad(output.square().sum(), x)
grad_reference, = torch.autograd.grad(reference.square().sum(), x)
assert torch.allclose(grad_ours, grad_reference, atol=1e-5)

# 题面示例：[1, 3] 标准化成 [-1, 1]
tiny_eps = LayerNorm(2, eps=1e-12)
assert torch.allclose(tiny_eps(torch.tensor([[1.0, 3.0]])), torch.tensor([[-1.0, 1.0]]))

# D = 1：输出有限，且等于 beta
single = LayerNorm(1)
with torch.no_grad():
    single.beta.fill_(0.5)
single_output = single(torch.tensor([[2.0], [-7.0]]))
assert torch.isfinite(single_output).all()
assert torch.allclose(single_output, torch.full((2, 1), 0.5))

# 低精度输入：输出 dtype 和输入一致
half_input = torch.randn(3, 4).to(torch.bfloat16)
assert LayerNorm(4)(half_input).dtype == torch.bfloat16

# 全零向量靠 eps 不会除零
assert torch.equal(LayerNorm(3)(torch.zeros(1, 3)), torch.zeros(1, 3))

# 非法参数
expect_value_error(lambda: LayerNorm(0))
expect_value_error(lambda: LayerNorm(4, eps=0.0))
