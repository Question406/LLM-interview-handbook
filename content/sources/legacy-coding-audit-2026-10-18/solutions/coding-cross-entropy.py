import torch
import torch.nn.functional as F


def cross_entropy_logits(logits, target, ignore_index=-100):
    """logits [N, V]，target [N] -> 未忽略样本上的平均交叉熵（标量）。"""
    if logits.ndim != 2 or logits.shape[1] < 1 or target.shape != logits.shape[:1]:
        raise ValueError(f"expected logits [N, V] and target [N], got {tuple(logits.shape)} and {tuple(target.shape)}")
    keep = target != ignore_index
    if not bool(keep.any()):
        return logits.sum() * 0.0  # 保留计算图，梯度为 0

    chosen = target[keep]
    num_classes = logits.shape[1]
    if bool(((chosen < 0) | (chosen >= num_classes)).any()):
        raise ValueError(f"target outside [0, {num_classes})")

    z = logits[keep].float()  # 低精度输入升到 fp32
    shifted = z - z.max(dim=-1, keepdim=True).values
    log_probs = shifted - shifted.exp().sum(dim=-1, keepdim=True).log()
    return -log_probs.gather(1, chosen[:, None]).mean()


def lm_ce(logits, labels, ignore_index=-100):
    """causal LM 损失：logits [B, L, V]，labels [B, L]；位置 t 预测 t+1，只 shift 一次。"""
    vocab = logits.size(-1)
    return cross_entropy_logits(
        logits[:, :-1].reshape(-1, vocab),
        labels[:, 1:].reshape(-1),
        ignore_index,
    )


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


torch.manual_seed(0)

# 两类均匀 logits：损失是 ln 2
uniform = torch.zeros(2, 2)
assert torch.isclose(cross_entropy_logits(uniform, torch.tensor([1, 99]), 99), torch.log(torch.tensor(2.0)))

# 与 PyTorch 一致；ignore_index 大于 V 也安全，被忽略的行梯度为 0
logits = torch.randn(4, 5, requires_grad=True)
target = torch.tensor([1, 99, 2, 99])
loss = cross_entropy_logits(logits, target, 99)
assert torch.allclose(loss, F.cross_entropy(logits, target, ignore_index=99))
loss.backward()
assert torch.all(logits.grad[[1, 3]] == 0)

# 全部忽略：返回 0，可以反传，梯度全为 0
logits = torch.randn(2, 3, requires_grad=True)
loss = cross_entropy_logits(logits, torch.tensor([99, 99]), 99)
loss.backward()
assert loss.item() == 0
assert torch.all(logits.grad == 0)

# 极端 logits 不会溢出成 inf / NaN
extreme = torch.tensor([[1000.0, -1000.0]])
assert torch.isclose(cross_entropy_logits(extreme, torch.tensor([0])), torch.tensor(0.0))
assert torch.isclose(cross_entropy_logits(extreme, torch.tensor([1])), torch.tensor(2000.0))

# causal LM：只 shift 一次
logits = torch.randn(2, 4, 5)
ids = torch.randint(0, 5, (2, 4))
expected = F.cross_entropy(logits[:, :-1].reshape(-1, 5), ids[:, 1:].reshape(-1))
assert torch.allclose(lm_ce(logits, ids), expected)

# 序列长度 1：没有可预测的位置，返回 0
assert lm_ce(torch.randn(2, 1, 5), torch.zeros(2, 1, dtype=torch.long)).item() == 0

# 未忽略的标签越界、形状不符
expect_value_error(cross_entropy_logits, torch.randn(2, 3), torch.tensor([0, 3]))
expect_value_error(cross_entropy_logits, torch.randn(2, 3), torch.tensor([0]))
