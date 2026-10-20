import torch
import torch.nn.functional as F


def fused_linear_ce(h, weight, target, ignore_index=-100, chunk=4096):
    """沿词表分块的 linear + cross entropy 前向。

    h: [N, D]，weight: [V, D]，target: [N]。不分配完整的 [N, V] logits，
    返回未忽略目标上的平均损失。
    """
    if type(chunk) is not int or chunk < 1:
        raise ValueError(f"chunk must be a positive int, got {chunk!r}")
    num_rows, vocab = h.size(0), weight.size(0)
    keep = target != ignore_index
    if bool((((target < 0) | (target >= vocab)) & keep).any()):
        raise ValueError(f"target outside [0, {vocab})")

    h32 = h.float()
    w32 = weight.float()
    running_max = h32.new_full((num_rows,), float("-inf"))  # [N]
    running_sum = h32.new_zeros(num_rows)                     # [N]，以 running_max 为基准
    for start in range(0, vocab, chunk):
        logits = h32 @ w32[start : start + chunk].T           # [N, C]
        new_max = torch.maximum(running_max, logits.amax(dim=-1))
        running_sum = running_sum * torch.exp(running_max - new_max) + torch.exp(logits - new_max[:, None]).sum(-1)
        running_max = new_max

    if not bool(keep.any()):
        return (h.sum() + weight.sum()) * 0.0  # 保留到 h 和 weight 的计算图

    safe_target = torch.where(keep, target, torch.zeros_like(target))
    target_logit = (h32 * w32[safe_target]).sum(-1)          # [N]，z_y = h · w_y
    nll = -target_logit + running_max + running_sum.log()
    return nll[keep].mean()


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(2)
h = torch.randn(3, 4, requires_grad=True)
w = torch.randn(7, 4, requires_grad=True)
target = torch.tensor([1, 99, 6])

# 不同 chunk（含 1、不整除 V、大于 V）的损失和梯度都与未融合版本一致
for chunk in (1, 3, 20):
    fused = fused_linear_ce(h, w, target, ignore_index=99, chunk=chunk)
    reference = F.cross_entropy(h @ w.T, target, ignore_index=99)
    assert torch.allclose(fused, reference, atol=1e-6)
    fused_grads = torch.autograd.grad(fused, (h, w))
    reference_grads = torch.autograd.grad(reference, (h, w))
    for got, want in zip(fused_grads, reference_grads):
        assert torch.allclose(got, want, atol=1e-6)

# 全部忽略：返回 0，h 和 weight 的梯度都是 0
zero = fused_linear_ce(h, w, torch.full((3,), 99), ignore_index=99, chunk=2)
assert zero == 0
for grad in torch.autograd.grad(zero, (h, w)):
    assert torch.all(grad == 0)

# 很大的 logits 也不溢出
big_h = torch.tensor([[100.0, 0.0]])
big_w = torch.tensor([[10.0, 0.0], [0.0, 1.0]])
assert torch.isclose(fused_linear_ce(big_h, big_w, torch.tensor([0]), chunk=1), torch.tensor(0.0), atol=1e-6)

# 非法 chunk、越界目标
expect_value_error(fused_linear_ce, h, w, target, ignore_index=99, chunk=0)
expect_value_error(fused_linear_ce, h, w, torch.tensor([0, 1, 7]))
