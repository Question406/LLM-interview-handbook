import torch
import torch.nn.functional as F


def _upcast(z):
    """fp16 / bf16 / 整数升到 float32，float64 保持不变。"""
    return z.to(torch.promote_types(z.dtype, torch.float32))


def logsumexp(z, dim=-1, keepdim=False):
    """数值稳定的 log(sum(exp(z)))；整行都是 -inf 时返回 -inf。"""
    z = _upcast(z)
    if z.shape[dim] == 0:
        raise ValueError(f"cannot reduce over empty dim {dim}")
    row_max = z.amax(dim=dim, keepdim=True)
    # 全 -inf 行的最大值是 -inf，直接相减会得到 -inf - (-inf) = NaN，改用 0 做平移
    shift = torch.where(torch.isfinite(row_max), row_max, torch.zeros_like(row_max))
    out = shift + (z - shift).exp().sum(dim=dim, keepdim=True).log()
    return out if keepdim else out.squeeze(dim)


def log_softmax(z, dim=-1):
    """z - logsumexp(z)；每行至少要有一个有限 logit。"""
    z = _upcast(z)
    row_max = z.amax(dim=dim, keepdim=True)
    if not torch.isfinite(row_max).all():
        raise ValueError("log_softmax needs at least one finite logit per row")
    shifted = z - row_max
    return shifted - shifted.exp().sum(dim=dim, keepdim=True).log()


def nll_from_logits(logits, target):
    """每个样本的交叉熵 -log softmax(logits)[target]。logits: [N, V]，target: [N]。"""
    num_classes = logits.shape[-1]
    if target.min() < 0 or target.max() >= num_classes:
        raise ValueError(f"target must be in [0, {num_classes}), "
                         f"got range [{target.min()}, {target.max()}]")
    log_probs = log_softmax(logits, dim=-1)                       # [N, V]
    return -log_probs.gather(1, target.unsqueeze(1)).squeeze(1)  # [N]


import math


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
logits = torch.tensor([[1000.0, 1001.0], [-1000.0, -999.0]])

# 大正数和大负数 logit 都不溢出，结果和 PyTorch 一致
assert torch.allclose(logsumexp(logits), torch.logsumexp(logits, -1))
assert torch.allclose(log_softmax(logits), F.log_softmax(logits, -1))

# 示例：logsumexp([1000, 1000]) = 1000 + ln 2
pair = logsumexp(torch.tensor([1000.0, 1000.0]))
assert torch.allclose(pair, torch.tensor(1000.0 + math.log(2)))

# 全 -inf 的一行：logsumexp 返回 -inf 而不是 NaN
all_masked = torch.full((1, 2), -float("inf"))
assert torch.isneginf(logsumexp(all_masked)).all()

# keepdim=True 保留被约简的维度，可以直接广播回原形状
assert logsumexp(logits, dim=-1, keepdim=True).shape == (2, 1)

# float64 不被降成 float32
assert logsumexp(logits.double()).dtype == torch.float64

# 交叉熵：在 log 空间按 target 取值，和 F.cross_entropy 一致
target = torch.tensor([1, 0])
expected = F.cross_entropy(logits, target, reduction="none")
assert torch.allclose(nll_from_logits(logits, target), expected)

# 非法输入：log_softmax 遇到全屏蔽行；target 越界；在空维度上约简
expect_value_error(log_softmax, all_masked)
expect_value_error(nll_from_logits, logits, torch.tensor([2, 0]))
expect_value_error(logsumexp, torch.empty(3, 0))
