import torch


def rloo_advantage(rewards, G):
    """RLOO advantage：每条回答减去同组其余 G - 1 条奖励的均值，不做 std 归一。

    rewards: [B * G]，按 repeat_interleave 排布，即每个 prompt 的 G 条 rollout 连续。
    返回同形状 [B * G]。
    """
    if G < 2:
        raise ValueError(f"leave-one-out needs G >= 2, got {G}")
    if rewards.numel() % G != 0:
        raise ValueError(f"{rewards.numel()} rewards cannot be split into groups of {G}")
    grouped = rewards.reshape(-1, G)                                  # [B, G]
    baseline = (grouped.sum(dim=1, keepdim=True) - grouped) / (G - 1)
    return (grouped - baseline).reshape(-1)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


torch.set_num_threads(1)

# 两个 prompt 各 3 条：第一组 [1, 0, 0] -> [1, -0.5, -0.5]；奖励全相同的组 advantage 全 0
rewards = torch.tensor([1.0, 0.0, 0.0, 4.0, 4.0, 4.0])
adv = rloo_advantage(rewards, 3)
assert torch.allclose(adv, torch.tensor([1.0, -0.5, -0.5, 0.0, 0.0, 0.0]))

# 每组 advantage 之和为 0，不同 prompt 不混组
assert torch.allclose(adv.reshape(-1, 3).sum(-1), torch.zeros(2))

# 等于 G / (G - 1) 倍的「减组均值」
grouped = rewards.reshape(-1, 3)
centered = (grouped - grouped.mean(dim=1, keepdim=True)).reshape(-1)
assert torch.allclose(adv, centered * 3 / 2)

# G = 2：两条互为 baseline
assert torch.allclose(rloo_advantage(torch.tensor([3.0, 1.0]), 2), torch.tensor([2.0, -2.0]))

# G < 2 或长度不能整除 G 时报错
expect_value_error(rloo_advantage, rewards, 1)
expect_value_error(rloo_advantage, rewards, 4)
