import torch


@torch.no_grad()
def gae(rewards, values, dones, last_value, gamma=0.99, lam=0.95):
    """反向递推 GAE。所有输入都是 [T]；last_value 是 V(s_T)，用于截断时自举。

    返回 (advantages, returns)，returns = advantages + values，不带梯度。
    """
    num_steps = len(rewards)
    advantages = torch.zeros_like(rewards)
    next_advantage = 0.0
    for t in reversed(range(num_steps)):
        next_value = values[t + 1] if t + 1 < num_steps else last_value
        not_done = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_value * not_done - values[t]
        next_advantage = delta + gamma * lam * not_done * next_advantage
        advantages[t] = next_advantage
    return advantages, advantages + values


def value_loss(v_pred, v_old, returns, mask, clip=0.2):
    """带 value clip 的 0.5 * MSE，按 mask 求平均；取两种误差中较大的一个。"""
    v_clipped = v_old + (v_pred - v_old).clamp(-clip, clip)
    unclipped_error = (v_pred - returns) ** 2
    clipped_error = (v_clipped - returns) ** 2
    loss = torch.maximum(unclipped_error, clipped_error)
    return 0.5 * (loss * mask).sum() / mask.sum().clamp(min=1)


torch.set_num_threads(1)

# 第二步 terminal：A = [1 + 2, 2]，values 为 0 时 returns 等于 advantages
advantages, returns = gae(torch.tensor([1.0, 2.0]), torch.zeros(2),
                          torch.tensor([0.0, 1.0]), 0.0, gamma=1.0, lam=1.0)
assert torch.equal(advantages, torch.tensor([3.0, 2.0]))
assert torch.equal(advantages, returns)

# 截断：没有 terminal，用 last_value 自举
advantages, _ = gae(torch.tensor([1.0]), torch.zeros(1), torch.zeros(1),
                    5.0, gamma=1.0, lam=1.0)
assert advantages.item() == 6

# 最后一步是 terminal 时 last_value 被屏蔽
advantages, _ = gae(torch.tensor([1.0]), torch.zeros(1), torch.ones(1),
                    5.0, gamma=1.0, lam=1.0)
assert advantages.item() == 1

# 中间的 terminal 阻止下一个回合的奖励反向泄漏
advantages, _ = gae(torch.tensor([1.0, 100.0]), torch.zeros(2), torch.ones(2),
                    0.0, gamma=1.0, lam=1.0)
assert torch.equal(advantages, torch.tensor([1.0, 100.0]))

# lam = 0 退化成一步 TD：A_t = r_t + gamma * V_{t+1} - V_t
advantages, _ = gae(torch.tensor([1.0, 1.0]), torch.tensor([0.5, 2.0]),
                    torch.zeros(2), 3.0, gamma=0.5, lam=0.0)
assert torch.allclose(advantages, torch.tensor([1.0 + 0.5 * 2.0 - 0.5, 1.0 + 0.5 * 3.0 - 2.0]))

# returns 不带梯度，即使 values 来自 critic 前向
critic_values = torch.zeros(2, requires_grad=True)
_, returns = gae(torch.ones(2), critic_values, torch.zeros(2), 0.0)
assert not returns.requires_grad

# value clip 取较大的误差：预测 0.4 被裁到 0.2，误差 (0.2 - 1)^2 = 0.64 胜出
v_pred = torch.tensor([0.4], requires_grad=True)
loss = value_loss(v_pred, torch.zeros(1), torch.ones(1), torch.ones(1))
assert torch.isfinite(loss)
assert torch.isclose(loss, torch.tensor(0.32))

# mask 全 0 时损失为 0，不会除以 0
loss = value_loss(v_pred, torch.zeros(1), torch.ones(1), torch.zeros(1))
assert loss.item() == 0
