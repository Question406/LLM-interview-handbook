import torch
from torch import nn
import torch.nn.functional as F


def llama_ffn_hidden(dim, multiple_of=256, ffn_mult=None):
    """Llama 的 FFN 中间维：floor(8D/3)，可选乘 ffn_mult，再向上对齐到 multiple_of。"""
    hidden = int(2 * 4 * dim / 3)  # 8/3 D
    if ffn_mult is not None:
        hidden = int(ffn_mult * hidden)
    return multiple_of * ((hidden + multiple_of - 1) // multiple_of)


class SwiGLU(nn.Module):
    """Llama MLP：down(silu(gate(x)) * up(x))，三个线性层都没有 bias。"""

    def __init__(self, dim, hidden=None):
        super().__init__()
        hidden = llama_ffn_hidden(dim) if hidden is None else hidden
        self.w_gate = nn.Linear(dim, hidden, bias=False)
        self.w_up = nn.Linear(dim, hidden, bias=False)
        self.w_down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        # x: [..., D] -> [..., D]
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))


torch.set_num_threads(1)
torch.manual_seed(0)

# Llama 7B 和 70B 的中间维
assert llama_ffn_hidden(4096) == 11008
assert llama_ffn_hidden(8192, multiple_of=4096, ffn_mult=1.3) == 28672

# 默认 hidden 走 llama_ffn_hidden
assert SwiGLU(48).w_gate.out_features == llama_ffn_hidden(48)

# 输出与按公式手算一致，形状不变
module = SwiGLU(4, hidden=6)
x = torch.randn(2, 3, 4, requires_grad=True)
y = module(x)
gate = F.silu(F.linear(x, module.w_gate.weight))
up = F.linear(x, module.w_up.weight)
expected = F.linear(gate * up, module.w_down.weight)
assert y.shape == x.shape
assert torch.allclose(y, expected)

# 没有 bias，三个权重都有梯度
assert all(layer.bias is None for layer in (module.w_gate, module.w_up, module.w_down))
y.sum().backward()
assert all(param.grad is not None for param in module.parameters())

# 先乘后激活是错的写法，结果不同
wrong = F.linear(F.silu(F.linear(x, module.w_gate.weight) * up), module.w_down.weight)
assert not torch.allclose(y, wrong)
