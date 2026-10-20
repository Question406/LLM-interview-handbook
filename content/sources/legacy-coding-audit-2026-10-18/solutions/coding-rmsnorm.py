import torch
from torch import nn


class RMSNorm(nn.Module):
    """沿最后一维的 RMSNorm：y = weight * x / sqrt(mean(x^2) + eps)，不减均值、没有 bias。"""

    def __init__(self, dim, eps=1e-6):
        super().__init__()
        if not eps > 0:
            raise ValueError(f"eps must be positive, got {eps}")
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        # x: [..., D]；在 float32 里算统计量，输出转回输入 dtype
        x32 = x.float()
        inv_rms = torch.rsqrt(x32.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return (x32 * inv_rms * self.weight).to(x.dtype)


def vs_layernorm(x, eps=1e-6):
    """返回 (无仿射 LayerNorm, 无仿射 RMSNorm)，用来对比两者差在减均值。"""
    mean = x.mean(-1, keepdim=True)
    layer_norm = (x - mean) * torch.rsqrt(x.var(-1, keepdim=True, unbiased=False) + eps)
    rms_norm = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps)
    return layer_norm, rms_norm


torch.manual_seed(0)

# 与公式一致，并且能反传
norm = RMSNorm(4)
x = torch.randn(2, 3, 4, requires_grad=True)
y = norm(x)
reference = x * torch.rsqrt(x.square().mean(-1, keepdim=True) + norm.eps) * norm.weight
assert torch.allclose(y, reference)
y.sum().backward()
assert torch.isfinite(x.grad).all()

# 例子 [3, 4]：分母是 sqrt(12.5 + eps)
assert torch.allclose(RMSNorm(2)(torch.tensor([3.0, 4.0])), torch.tensor([3.0, 4.0]) / 12.5 ** 0.5, atol=1e-5)

# 零向量：eps 保护，输出仍是 0
assert torch.all(norm(torch.zeros(2, 4)) == 0)

# 输出 dtype 跟随输入
assert norm(torch.ones(2, 4, dtype=torch.float16)).dtype == torch.float16

# 与 LayerNorm 的区别：均值非零时结果不同，均值为 0 时相同
layer_norm, rms_norm = vs_layernorm(torch.tensor([[3.0, 4.0]]))
assert torch.allclose(layer_norm, torch.tensor([[-1.0, 1.0]]), atol=1e-4)
assert not torch.allclose(layer_norm, rms_norm)
layer_norm, rms_norm = vs_layernorm(torch.tensor([[-2.0, 2.0]]))
assert torch.allclose(layer_norm, rms_norm)

# eps 必须为正
try:
    RMSNorm(4, eps=0)
except ValueError:
    pass
else:
    raise AssertionError("eps=0 accepted")
