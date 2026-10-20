import numpy as np


def as_distribution(values):
    """校验并返回一维概率向量：非负、有限、和为 1。"""
    probs = np.asarray(values, dtype=float)
    if probs.ndim != 1 or len(probs) == 0:
        raise ValueError("distribution must be a non-empty 1-D vector")
    if not np.isfinite(probs).all() or np.any(probs < 0):
        raise ValueError("distribution must be finite and non-negative")
    if not np.isclose(probs.sum(), 1):
        raise ValueError("distribution must sum to 1")
    return probs / probs.sum()


def sample(rng, probs):
    return int(rng.choice(len(probs), p=probs))


def residual_sample(rng, p, q):
    """拒绝后从 max(p - q, 0) 归一化后的分布里重新采样。"""
    residual = np.maximum(p - q, 0)
    total = residual.sum()
    if total <= 0:
        # p == q 时接受概率恒为 1，不可能走到这里
        raise ArithmeticError("rejection with an empty residual")
    return sample(rng, residual / total)


def speculative(target_batch, draft_next, limit, block, rng, eos=-1):
    """投机采样，返回 (生成的 token 列表, target 调用次数)。

    draft_next(prefix) -> q：draft 模型在 prefix 之后的下一 token 分布。
    target_batch(prefix, candidates) -> [p_0, ..., p_K]：p_i 条件于 prefix + candidates[:i]，
    一次调用验证 K 个候选，并多给一个分布用于全部接受后的补采样。
    EOS 不进入输出；limit == 0 时不调用任何模型。
    """
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if block < 1:
        raise ValueError("block must be >= 1")

    output = []
    target_calls = 0
    while len(output) < limit:
        # 1. draft 依次提出最多 block 个候选，遇到 EOS 就停
        proposed = []
        draft_probs = []
        for _ in range(min(block, limit - len(output))):
            q = as_distribution(draft_next(output + proposed))
            token = sample(rng, q)
            draft_probs.append(q)
            proposed.append(token)
            if token == eos:
                break

        # 2. target 一次性给出每个位置的分布
        target_probs = [as_distribution(p) for p in target_batch(list(output), proposed)]
        target_calls += 1
        if len(target_probs) != len(proposed) + 1:
            raise ValueError("target_batch must return len(candidates) + 1 distributions")
        if any(p.shape != draft_probs[0].shape for p in target_probs):
            raise ValueError("target and draft vocabularies differ")

        # 3. 逐个验证：以 min(1, p/q) 接受；第一次拒绝时从残差分布重采样并丢弃后面的候选
        all_accepted = True
        for token, q, p in zip(proposed, draft_probs, target_probs):
            if rng.random() < min(1.0, p[token] / q[token]):
                chosen = token
            else:
                chosen = residual_sample(rng, p, q)
                all_accepted = False
            if chosen == eos:
                return output, target_calls
            output.append(chosen)
            if len(output) >= limit:
                return output, target_calls
            if not all_accepted:
                break

        # 4. 全部接受时，target 的最后一个分布还能免费多采一个 token
        if all_accepted:
            extra = sample(rng, target_probs[-1])
            if extra == eos:
                return output, target_calls
            output.append(extra)
    return output, target_calls


def test():
    rng = np.random.default_rng(5)

    # draft 偏向 token 1，target 偏向 token 0：首个 token 的分布应服从 target（约 0.8）
    target_dist = np.array([0.8, 0.2])
    draft_dist = np.array([0.2, 0.8])

    def biased_target(prefix, candidates):
        return [target_dist] * (len(candidates) + 1)

    def biased_draft(prefix):
        return draft_dist

    firsts = [speculative(biased_target, biased_draft, 1, 3, rng)[0][0] for _ in range(6000)]
    assert abs(firsts.count(0) / len(firsts) - 0.8) < 0.025

    # limit == 0 时不调用 target
    assert speculative(biased_target, biased_draft, 0, 3, rng) == ([], 0)

    # draft 与 target 完全一致时全部接受：每轮 3 个候选 + 1 个补采样，10 个 token 需要 3 轮
    certain = np.array([1.0, 0.0])

    def certain_target(prefix, candidates):
        return [certain] * (len(candidates) + 1)

    output, calls = speculative(certain_target, lambda prefix: certain, 10, 3, rng)
    assert output == [0] * 10
    assert calls == 3

    # EOS 不进入输出
    eos_dist = np.array([0.0, 1.0])
    output, calls = speculative(
        lambda prefix, candidates: [eos_dist] * (len(candidates) + 1),
        lambda prefix: eos_dist,
        10, 3, rng, eos=1,
    )
    assert output == []
    assert calls == 1


if __name__ == "__main__":
    test()
