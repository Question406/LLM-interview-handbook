import numpy as np

STD_FLOOR = 1e-8


def advantages(rewards):
    """组内归一化优势。rewards: (P, G)，每行是同一个 prompt 的 G 个回答的得分。

    每组减去组均值、除以组内总体标准差；一组得分全相同（std < 1e-8）时优势全为 0，不除零。
    """
    rewards = np.asarray(rewards, dtype=float)
    if rewards.ndim != 2 or rewards.shape[1] == 0:
        raise ValueError(f"rewards must have shape (P, G) with G >= 1, got {rewards.shape}")
    centered = rewards - rewards.mean(axis=1, keepdims=True)
    std = rewards.std(axis=1, keepdims=True)
    return np.divide(centered, std, out=np.zeros_like(centered), where=std >= STD_FLOOR)


def _check_loss_inputs(new_logp, old_logp, adv, mask, eps):
    if new_logp.ndim != 2:
        raise ValueError(f"logprobs must be 2-D (B, T), got {new_logp.shape}")
    if old_logp.shape != new_logp.shape or mask.shape != new_logp.shape:
        raise ValueError("new_logp, old_logp and mask must have the same shape")
    if adv.shape != (len(new_logp),):
        raise ValueError(f"adv must have shape ({len(new_logp)},), got {adv.shape}")
    if not 0 < eps < 1:
        raise ValueError(f"eps must be in (0, 1), got {eps}")


def loss_grad(new_logp, old_logp, adv, mask, eps=0.2):
    """PPO 式 clipped surrogate 的损失（取负，用于最小化）和它对 new_logp 的梯度。

    new_logp, old_logp, mask: (B, T)，B = P * G，是被采样 token 的 log 概率；adv: (B,)。
    old_logp 和 adv 视为常量；损失对 mask 内的有效 token 求平均；不含参考模型 KL。
    """
    new_logp = np.asarray(new_logp, dtype=float)
    old_logp = np.asarray(old_logp, dtype=float)
    adv = np.asarray(adv, dtype=float)
    mask = np.asarray(mask, dtype=bool)
    _check_loss_inputs(new_logp, old_logp, adv, mask, eps)

    num_tokens = int(mask.sum())
    if num_tokens == 0:
        return 0.0, np.zeros_like(new_logp)

    adv = adv[:, None]  # (B, 1)，广播到每个 token
    ratio = np.exp(new_logp - old_logp)  # 重要性采样比 π_new / π_old
    unclipped = ratio * adv
    clipped = np.clip(ratio, 1 - eps, 1 + eps) * adv
    loss = float((-np.minimum(unclipped, clipped) * mask).sum() / num_tokens)

    # 只有当 clip 阻止策略继续往「有利方向」移动时梯度才为 0：
    # 正优势且 ratio 已超过 1+eps，或负优势且 ratio 已低于 1-eps。
    flat = ((adv > 0) & (ratio > 1 + eps)) | ((adv < 0) & (ratio < 1 - eps))
    grad = -adv * ratio * ~flat * mask / num_tokens  # d ratio / d new_logp = ratio
    return loss, grad


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 第一组得分相同，优势全 0；第二组标准化为 -1 和 1
    assert np.allclose(advantages([[1, 1], [0, 2]]), [[0, 0], [-1, 1]])

    # 解析梯度和中心差分对照；第二行的两个 token 分别落在 clip 平坦区和非平坦区
    new_logp = np.array([[0.05, -0.1], [0.4, -0.5]])
    old_logp = np.zeros_like(new_logp)
    adv = np.array([1.0, -1.0])
    mask = np.array([[1, 0], [1, 1]], dtype=bool)
    _, grad = loss_grad(new_logp, old_logp, adv, mask)
    step = 1e-6
    for i in range(2):
        for j in range(2):
            plus = new_logp.copy()
            minus = new_logp.copy()
            plus[i, j] += step
            minus[i, j] -= step
            loss_plus = loss_grad(plus, old_logp, adv, mask)[0]
            loss_minus = loss_grad(minus, old_logp, adv, mask)[0]
            numeric = (loss_plus - loss_minus) / (2 * step)
            assert np.isclose(numeric, grad[i, j], atol=1e-7)

    # new == old 时 ratio 为 1，损失等于负的平均优势
    loss, _ = loss_grad(old_logp, old_logp, adv, mask)
    assert np.isclose(loss, -(1 + (-1) + (-1)) / 3)

    # 全部 mask 掉时损失为 0
    assert loss_grad(new_logp, old_logp, adv, np.zeros_like(mask))[0] == 0

    # 形状和 eps 校验
    expect_value_error(advantages, [1, 2])
    expect_value_error(loss_grad, new_logp, old_logp, np.array([1.0]), mask)
    expect_value_error(loss_grad, new_logp, old_logp, adv, mask, 1.5)


if __name__ == "__main__":
    test()
