def greedy(verify, limit, eos=-1):
    """逐 token 贪心解码，返回 (输出 token 列表, 模型调用次数)。EOS 不放进输出。"""
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")
    out = []
    calls = 0
    while len(out) < limit:
        token = verify(out, [0])[0]  # 只要下一个 token，candidates 内容不影响第 0 个预测
        calls += 1
        if token == eos:
            break
        out.append(token)
    return out, calls


def edits(verify, draft, block, limit, eos=-1):
    """speculative edits：拿原代码 draft 当草稿，每次批量验证最多 block 个 token。

    verify(prefix, candidates)[i] 是以 prefix + candidates[:i] 为上下文时模型的 argmax。
    输出保证和 greedy 完全相同。返回 (输出 token 列表, 模型调用次数)。
    """
    if block < 1:
        raise ValueError(f"block must be >= 1, got {block}")
    if limit < 0:
        raise ValueError(f"limit must be non-negative, got {limit}")
    out = []
    pos = 0  # 下一个待验证的草稿位置
    calls = 0
    use_draft = True
    while len(out) < limit:
        if use_draft and pos < len(draft):
            candidates = list(draft[pos:pos + min(block, limit - len(out))])
            predictions = verify(out, candidates)
            calls += 1
            if len(predictions) != len(candidates):
                raise ValueError("verify must return one prediction per candidate")
            for candidate, prediction in zip(candidates, predictions):
                if prediction == eos:
                    return out, calls
                out.append(prediction)  # 无论是否匹配，模型的预测都是正确的下一个 token
                if prediction != candidate:
                    # 后面的预测建立在错误的草稿 token 上，全部作废；之后退回 greedy
                    use_draft = False
                    break
                pos += 1
        else:
            token = verify(out, [0])[0]
            calls += 1
            if token == eos:
                break
            out.append(token)
    return out, calls


def test():
    def make_verify(target):
        """依赖前缀的确定性模型：只有上下文是 target 的前缀时才继续预测 target，否则输出 EOS。"""

        def verify(prefix, candidates):
            predictions = []
            context = list(prefix)
            for candidate in candidates:
                n = len(context)
                if n < len(target) and context == target[:n]:
                    predictions.append(target[n])
                else:
                    predictions.append(-1)
                context.append(candidate)  # 错误的草稿 token 会改变后面的预测
            return predictions

        return verify

    # 各种草稿（空、全错、中间分歧、完全匹配）和长度上限下，输出都必须和 greedy 一致
    for target in ([], [1], [1, 2, 3, 4]):
        verify = make_verify(target)
        for draft in ([], [9], [1, 9, 3], target):
            for limit in range(7):
                assert edits(verify, draft, 2, limit)[0] == greedy(verify, limit)[0]

    # 草稿中途分歧：输出模型的修正 token，然后继续贪心
    verify = make_verify([1, 2, 3])
    assert edits(verify, [1, 9, 3], 2, 10)[0] == [1, 2, 3]

    # 草稿完全正确时，批量验证的调用次数少于逐 token 贪心
    verify = make_verify(list(range(6)))
    assert edits(verify, list(range(6)), 3, 10)[1] < greedy(verify, 10)[1]

    # limit = 0 不调用模型
    assert edits(verify, list(range(6)), 3, 0) == ([], 0)


if __name__ == "__main__":
    test()
