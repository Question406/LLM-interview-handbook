import torch
import torch.nn.functional as F


def token_kl_full(logits, logits_ref, mask):
    """全词表 KL(π || π_ref) 在有效 token 上的平均。logits*: [B, T, V]；mask: [B, T]，True 为有效。"""
    log_pi = F.log_softmax(logits.float(), dim=-1)
    log_ref = F.log_softmax(logits_ref.float(), dim=-1)
    kl = (log_pi.exp() * (log_pi - log_ref)).sum(dim=-1)  # [B, T]
    if not bool(mask.any()):
        return logits.sum() * 0.0  # 空 mask：返回可反传的 0，不是 NaN
    return kl[mask].mean()


def token_kl_sampled(logp, logp_ref, mask):
    """采样 token 的 log-ratio 平均，是 KL 的蒙特卡洛估计。logp*: [B, T]。"""
    if not bool(mask.any()):
        return logp.sum() * 0.0
    return (logp - logp_ref).float()[mask].mean()


def kl_div_footgun(log_pi, log_ref):
    """[N, V]。返回 (batchmean 的正确 KL, reduction='mean' 的错误值)。"""
    pi = log_pi.exp()
    correct = F.kl_div(log_ref, pi, reduction="batchmean", log_target=False)
    wrong_mean = F.kl_div(log_ref, pi, reduction="mean")  # 多除了一个 V
    return correct, wrong_mean


torch.set_num_threads(1)

pi = torch.tensor([[[0.75, 0.25]]])
ref = torch.tensor([[[0.5, 0.5]]])
mask = torch.ones(1, 1, dtype=torch.bool)

# 全词表 KL 等于按定义手算的值
kl = token_kl_full(pi.log(), ref.log(), mask)
expected = (pi * (pi.log() - ref.log())).sum()
assert torch.allclose(kl, expected)
assert abs(kl.item() - 0.130812) < 1e-5

# 两个分布相同时 KL 为 0
assert token_kl_full(pi.log(), pi.log(), mask) == 0

# 空 mask 返回 0，且梯度为 0
logits = pi.log().requires_grad_()
empty = token_kl_full(logits, ref.log(), torch.zeros_like(mask))
assert empty == 0
assert torch.all(torch.autograd.grad(empty, logits)[0] == 0)

# pad token 不进分母
logits2 = torch.cat([pi.log(), ref.log()], dim=1)  # 第 2 个位置 KL = 0
ref2 = torch.cat([ref.log(), ref.log()], dim=1)
keep_first = torch.tensor([[True, False]])
assert torch.allclose(token_kl_full(logits2, ref2, keep_first), expected)

# 采样估计的单样本值可以为负
assert token_kl_sampled(torch.tensor([[-2.0]]), torch.tensor([[-1.0]]), mask) == -1

# batchmean 等于真实 KL，mean 恰好小 V 倍
correct, wrong = kl_div_footgun(pi.log()[0], ref.log()[0])
assert torch.allclose(correct, expected)
assert torch.allclose(wrong * 2, correct)
