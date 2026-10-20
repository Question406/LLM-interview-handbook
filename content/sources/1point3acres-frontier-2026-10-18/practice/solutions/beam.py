import math


def beam_search(next_logprobs, start, eos, width, max_new):
    """逐步 beam search，返回 [(tokens, score), ...]，按分数降序。

    next_logprobs(tokens) 返回词表上每个 token 的 log 概率。
    已经生成 EOS 的 beam 不再扩展，原样参与后续排序；没有长度惩罚。
    分数相同时按 token 序列的字典序排，保证结果确定。
    """
    if width < 1:
        raise ValueError(f"width must be >= 1, got {width}")
    if max_new < 0:
        raise ValueError(f"max_new must be >= 0, got {max_new}")

    # 每个 beam 是 (tokens, 累计 log 概率, 是否已结束)
    beams = [(tuple(start), 0.0, False)]
    for _ in range(max_new):
        candidates = []
        for tokens, score, finished in beams:
            if finished:
                candidates.append((tokens, score, True))
                continue
            for token, logprob in enumerate(next_logprobs(list(tokens))):
                if math.isnan(logprob) or logprob > 1e-10:
                    raise ValueError(f"invalid log probability: {logprob}")
                if logprob == -math.inf:
                    continue  # 概率为 0 的扩展直接丢弃
                candidates.append((tokens + (token,), score + logprob, token == eos))

        # 所有候选放在一起全局截断，而不是每个 beam 各留 width 个
        candidates.sort(key=lambda beam: (-beam[1], beam[0]))
        beams = candidates[:width]
        if not beams or all(finished for _, _, finished in beams):
            break

    return [(list(tokens), score) for tokens, score, _ in beams]


def test():
    def constant_model(tokens):
        # 词表 {0, 1}，1 是 EOS；每一步 P(0) = 0.4，P(1) = 0.6
        return [math.log(0.4), math.log(0.6)]

    # width = 1 时就是贪心：第一步选 EOS 后停止
    result = beam_search(constant_model, [], 1, 1, 10)
    assert result[0][0] == [1]
    assert math.isclose(result[0][1], math.log(0.6))

    # width = 2：已结束的 [1] 保留，和新扩展的 [0, 1] 一起排序
    result = beam_search(constant_model, [], 1, 2, 2)
    assert [tokens for tokens, _ in result] == [[1], [0, 1]]

    # max_new = 0 时原样返回 start
    assert beam_search(constant_model, [8], 1, 1, 0) == [([8], 0.0)]

    # beam 足够宽时，2 步内的所有路径都应该出现
    result = beam_search(constant_model, [], 1, 8, 2)
    assert {tuple(tokens) for tokens, _ in result} == {(1,), (0, 1), (0, 0)}


if __name__ == "__main__":
    test()
