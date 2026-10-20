import math


def beam_search(next_logprobs, start, eos, width, max_new):
    """返回最多 width 条 (tokens, 累计 log-prob)，按分数降序、序列字典序升序。"""
    if width < 1:
        raise ValueError(f"width must be at least 1, got {width}")
    if max_new < 0:
        raise ValueError(f"max_new must be non-negative, got {max_new}")

    beams = [(tuple(start), 0.0, False)]  # (tokens, score, finished)
    for _ in range(max_new):
        candidates = []
        for tokens, score, finished in beams:
            if finished:
                candidates.append((tokens, score, True))  # EOS 之后不再扩展
                continue
            for token, logprob in enumerate(next_logprobs(list(tokens))):
                if math.isnan(logprob) or logprob > 1e-10:
                    raise ValueError(f"invalid log probability {logprob} for token {token}")
                if logprob != -math.inf:
                    candidates.append((tokens + (token,), score + logprob, token == eos))
        beams = sorted(candidates, key=lambda beam: (-beam[1], beam[0]))[:width]
        if not beams or all(finished for _, _, finished in beams):
            break
    return [(list(tokens), score) for tokens, score, _ in beams]


def rank_with_length_penalty(beams, prompt_length=0, alpha=0.6):
    """按 GNMT 长度惩罚 score / ((5 + 新 token 数) / 6) ** alpha 重新排序。"""
    if alpha < 0:
        raise ValueError(f"alpha must be non-negative, got {alpha}")

    def penalized(beam):
        tokens, score = beam
        new_length = len(tokens) - prompt_length
        return score / ((5 + new_length) / 6) ** alpha

    return sorted(beams, key=lambda beam: (-penalized(beam), beam[0]))


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}{args}")


def fixed(seq):
    return [math.log(0.4), math.log(0.6)]


def uniform(seq):
    return [math.log(0.5)] * 2


# EOS 后不再扩展；已结束的 [1] 仍然占一个 beam 位置
results = beam_search(fixed, [], 1, 2, 2)
assert [tokens for tokens, _ in results] == [[1], [0, 1]]

# max_new = 0 直接返回 prompt
assert beam_search(fixed, [9], 1, 2, 0) == [([9], 0.0)]

# 宽度足够时保留所有路径，但 [1] 之后不会出现 [1, 1]
results = beam_search(uniform, [], 1, 8, 2)
assert {tuple(tokens) for tokens, _ in results} == {(0, 0), (0, 1), (1,)}
assert [1, 1] not in [tokens for tokens, _ in results]

# width = 1 就是 greedy
assert beam_search(fixed, [], 0, 1, 3) == [([1, 1, 1], 3 * math.log(0.6))]

# 被 -inf 禁用的 token 不会出现
results = beam_search(lambda seq: [-math.inf, 0.0], [], 5, 2, 2)
assert results == [([1, 1], 0.0)]

# 非法参数和非法 log 概率
expect_value_error(beam_search, fixed, [], 1, 0, 2)
expect_value_error(beam_search, fixed, [], 1, 2, -1)
expect_value_error(beam_search, lambda seq: [0.5, -1.0], [], 1, 2, 1)
expect_value_error(beam_search, lambda seq: [math.nan, -1.0], [], 1, 2, 1)

# 长度惩罚：累计分数相同时，长句排在前面
assert rank_with_length_penalty([([0], -1.0), ([0, 0], -1.0)])[0][0] == [0, 0]

# alpha = 0 时不惩罚，只按分数排
assert rank_with_length_penalty([([0, 0], -2.0), ([0], -1.0)], alpha=0)[0][0] == [0]
expect_value_error(rank_with_length_penalty, [([0], -1.0)], 0, -0.1)
