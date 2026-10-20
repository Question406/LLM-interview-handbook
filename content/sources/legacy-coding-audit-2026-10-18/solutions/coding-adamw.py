import torch
from torch import nn


def adamw_step(p, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, wd=0.01):
    """AdamW 的一步更新，不修改输入，返回 (新参数, 新 m, 新 v)。

    p, g, m, v 同形状；t 是从 1 开始的 optimizer step 计数。
    权重衰减直接作用在参数上（decoupled），不进入梯度和矩估计。
    """
    if t < 1:
        raise ValueError(f"step t starts at 1, got {t}")
    if not (0 <= b1 < 1 and 0 <= b2 < 1):
        raise ValueError(f"betas must be in [0, 1), got b1={b1}, b2={b2}")
    if eps <= 0:
        raise ValueError(f"eps must be positive, got {eps}")
    m = b1 * m + (1.0 - b1) * g
    v = b2 * v + (1.0 - b2) * g * g
    m_hat = m / (1.0 - b1 ** t)   # bias correction：早期 m、v 偏向 0
    v_hat = v / (1.0 - b2 ** t)
    p = p * (1.0 - lr * wd)       # decoupled decay，用更新前的参数
    p = p - lr * m_hat / (v_hat.sqrt() + eps)
    return p, m, v


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
params = torch.tensor([1.0, -2.0])
grad = torch.tensor([0.5, 0.25])
m0 = torch.zeros_like(params)
v0 = torch.zeros_like(params)

# 首步与 torch.optim.AdamW 一致
new_params, m1, v1 = adamw_step(params, grad, m0, v0, 1)
reference = nn.Parameter(params.clone())
optimizer = torch.optim.AdamW([reference], lr=0.001, weight_decay=0.01)
reference.grad = grad.clone()
optimizer.step()
assert torch.allclose(new_params, reference)

# 连续三步仍与 PyTorch 一致（检查 t 递增时的 bias correction）
current, m_state, v_state = new_params, m1, v1
for step in (2, 3):
    step_grad = grad * step
    current, m_state, v_state = adamw_step(current, step_grad, m_state, v_state, step)
    reference.grad = step_grad.clone()
    optimizer.step()
assert torch.allclose(current, reference)

# 梯度为 0 时只剩衰减：1 * (1 - 0.1 * 0.2) = 0.98
decayed, _, _ = adamw_step(torch.tensor([1.0]), torch.zeros(1), torch.zeros(1), torch.zeros(1), 1, lr=0.1, wd=0.2)
assert torch.allclose(decayed, torch.tensor([0.98]))

# 不修改输入
assert torch.equal(params, torch.tensor([1.0, -2.0]))
assert torch.equal(m0, torch.zeros(2))

# 非法超参数
expect_value_error(adamw_step, params, grad, m0, v0, 0)
expect_value_error(adamw_step, params, grad, m0, v0, 1, b2=1.0)
expect_value_error(adamw_step, params, grad, m0, v0, 1, eps=0.0)
