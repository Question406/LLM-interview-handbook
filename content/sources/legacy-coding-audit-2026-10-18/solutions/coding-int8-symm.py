import torch


def symm_quant_int8(x, dim=None):
    """对称 INT8 量化。dim=None 为 per-tensor，否则沿 dim 取 max（keepdim）。

    返回 (q: int8，与 x 同形状, scale: 正的浮点张量)。
    """
    if dim is None:
        amax = x.abs().amax()
    else:
        amax = x.abs().amax(dim=dim, keepdim=True)
    scale = (amax / 127.0).clamp_min(1e-12)
    q = (x / scale).round().clamp(-127, 127).to(torch.int8)
    return q, scale


def int8_linear(xq, wq, sx, sw):
    """INT8 线性层的数值参考：int32 累加后再乘两边的 scale。

    xq: [M, K] int8，wq: [N, K] int8；sx: 标量或 [M, 1]；sw: 标量、[N] 或 [N, 1]。
    返回 [M, N] float32。
    """
    acc = xq.to(torch.int32) @ wq.to(torch.int32).T  # [M, N] int32
    y = acc.float() * sx
    sw = torch.as_tensor(sw)
    if sw.numel() > 1:
        sw = sw.reshape(1, -1)  # [N] 或 [N, 1] -> [1, N]，沿输出通道广播
    return y * sw


def roundtrip_err(x, dim=None):
    """量化后再反量化的最大绝对误差。"""
    q, scale = symm_quant_int8(x, dim=dim)
    return (q.float() * scale - x).abs().max()


torch.set_num_threads(1)
x = torch.tensor([[0.0, 1.0, -2.0], [1.0, -0.2, 0.0]])
w = torch.tensor([[1.0, 0.0, -0.5], [-1.0, 0.5, 0.0]])

# per-token 激活 + per-channel 权重：结果接近浮点矩阵乘
xq, sx = symm_quant_int8(x, dim=1)
wq, sw = symm_quant_int8(w, dim=1)
y = int8_linear(xq, wq, sx, sw)
assert y.shape == (2, 2)
assert torch.allclose(y, x @ w.T, atol=0.04)

# 每行最大绝对值映射到 ±127，反量化误差不超过半格
assert xq.abs().amax(dim=1).tolist() == [127, 127]
assert torch.all((xq.float() * sx - x).abs() <= sx / 2 + 1e-6)

# 全 0 输入：量化结果全 0，scale 仍为正
q, scale = symm_quant_int8(torch.zeros(3))
assert torch.all(q == 0)
assert scale > 0

# per-tensor：两个标量 scale 也能得到同样的近似
xq, sx = symm_quant_int8(x)
wq, sw = symm_quant_int8(w)
assert sx.dim() == 0
assert torch.allclose(int8_linear(xq, wq, sx, sw), x @ w.T, atol=0.05)

# M = N 时 [N, 1] 的权重 scale 也必须沿列广播
x_square = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
w_rows = torch.tensor([[10.0, 0.0], [0.0, 1.0]])
xq, sx = symm_quant_int8(x_square, dim=1)
wq, sw = symm_quant_int8(w_rows, dim=1)
assert torch.allclose(int8_linear(xq, wq, sx, sw), x_square @ w_rows.T, atol=1e-4)

# roundtrip_err 与 scale / 2 的上界一致
assert roundtrip_err(torch.tensor([0.3, -1.0, 0.77])) <= 1.0 / 127 / 2 + 1e-6
