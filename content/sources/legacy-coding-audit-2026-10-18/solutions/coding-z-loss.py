import math

import torch

Z_COEF = 1e-4


def ce_with_z_loss(logits, target, ignore_index=-100, z_coef=Z_COEF):
    """交叉熵 + PaLM z-loss，只在有效 token 上平均。

    logits: [B, T, V]；target: [B, T]，取值是合法词表下标或 ignore_index（负数）。
    返回 (total, ce, z_loss)，其中 z_loss 是未乘系数的 mean(logZ^2)。
    全部 token 被忽略时三项都是 0，且仍可反传。
    """
    if z_coef < 0:
        raise ValueError(f"z_coef must be non-negative, got {z_coef}")
    x = logits.float()
    log_z = torch.logsumexp(x, dim=-1)                      # [B, T]
    logp = x - log_z.unsqueeze(-1)                          # [B, T, V]
    safe_target = target.clamp(min=0)                       # ignore 位置先换成 0，gather 后再 mask 掉
    nll = -logp.gather(-1, safe_target.unsqueeze(-1)).squeeze(-1)
    mask = target != ignore_index
    denom = mask.sum().clamp_min(1)
    ce = nll[mask].sum() / denom
    z_loss = (log_z.square() * mask).sum() / denom
    return ce + z_coef * z_loss, ce, z_loss


def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)
logits = torch.zeros(1, 1, 2, requires_grad=True)
target = torch.zeros(1, 1, dtype=torch.long)

# logits 全 0、V = 2：CE = ln 2，z_loss = (ln 2)^2，total = CE + 1e-4 * z_loss
total, ce, reg = ce_with_z_loss(logits, target)
assert torch.allclose(ce, torch.tensor(math.log(2)))
assert torch.allclose(reg, torch.tensor(math.log(2) ** 2))
assert torch.allclose(total, ce + 1e-4 * reg)

# 全部 ignore：三项都是 0，且可以反传、梯度为 0
all_ignored = ce_with_z_loss(logits, torch.full_like(target, -100))
assert all(value == 0 for value in all_ignored)
assert torch.all(torch.autograd.grad(all_ignored[0], logits)[0] == 0)

# logits 整体平移：CE 不变，z_loss 变大
_, shifted_ce, shifted_reg = ce_with_z_loss(logits + 50, target)
assert torch.allclose(ce, shifted_ce)
assert shifted_reg > reg

# ignore 位置不进分子也不进分母：加一个被忽略的 token，结果不变
two_logits = torch.cat([logits.detach(), torch.full((1, 1, 2), 30.0)], dim=1)
two_target = torch.tensor([[0, -100]])
_, ce_two, reg_two = ce_with_z_loss(two_logits, two_target)
assert torch.allclose(ce_two, ce)
assert torch.allclose(reg_two, reg)

# 系数为负报错
expect_value_error(ce_with_z_loss, logits, target, z_coef=-1.0)
