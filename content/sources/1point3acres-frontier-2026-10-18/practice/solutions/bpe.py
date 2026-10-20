import random


def encode(text, merges):
    """字节级 BPE。merges 按优先级从高到低排列，每轮只合并一对。

    每轮在所有相邻 token 对里找 rank 最小的（相同 rank 取最左），合并后重新找，
    直到没有可合并的对。返回 bytes token 列表。
    """
    ranks = {pair: rank for rank, pair in enumerate(merges)}
    if len(ranks) != len(merges):
        raise ValueError("merges must not contain duplicates")
    if any(not left or not right for left, right in merges):
        raise ValueError("merge parts must be non-empty bytes")

    tokens = [bytes([byte]) for byte in text.encode("utf-8")]
    while True:
        candidates = [
            (ranks[(tokens[i], tokens[i + 1])], i)
            for i in range(len(tokens) - 1)
            if (tokens[i], tokens[i + 1]) in ranks
        ]
        if not candidates:
            return tokens
        _, i = min(candidates)  # 先比 rank，再比位置
        tokens[i:i + 2] = [tokens[i] + tokens[i + 1]]


def decode(tokens):
    """拼回字节后按 UTF-8 严格解码。"""
    return b"".join(tokens).decode("utf-8")


def estimate(text, merges, budget, rng):
    """最多编码 budget 个字符，估计整段文本的 token 数。返回 (估计值, 实际编码的字符数)。

    文本不超过预算时直接精确计算；否则随机取若干个固定长度的字符窗口，
    用平均「token 数 / 字符数」乘以总字符数。窗口边界会切断跨窗口的合并，
    所以这个估计有偏差（通常偏高）。
    """
    if budget < 1:
        raise ValueError(f"budget must be at least 1: {budget}")
    if not text:
        return 0.0, 0
    if len(text) <= budget:
        return float(len(encode(text, merges))), len(text)

    window = min(32, budget)
    sampled_chars = 0
    sampled_tokens = 0
    while sampled_chars + window <= budget:
        start = rng.randrange(len(text) - window + 1)
        sampled_tokens += len(encode(text[start:start + window], merges))
        sampled_chars += window
    return sampled_tokens / sampled_chars * len(text), sampled_chars


def test():
    merges = [(b"a", b"b"), (b"ab", b"ab")]

    # 先合并 a+b，再合并 ab+ab
    assert encode("abab", merges) == [b"abab"]

    # 编码再解码要还原原文，包括多字节字符和 emoji
    for text in ("", "hello", "你好🙂", "abab"):
        assert decode(encode(text, merges)) == text

    # 相同 rank 取最左：aaa 只能合并前两个
    assert encode("aaa", [(b"a", b"a")]) == [b"aa", b"a"]

    # 文本不超过预算时精确计数
    assert estimate("abab", merges, 4, random.Random(1)) == (1.0, 4)

    # 超过预算时只编码不超过 budget 个字符
    estimated, sampled = estimate("abab" * 100, merges, 100, random.Random(3))
    assert estimated > 0
    assert sampled <= 100

    # 非法 merges
    try:
        encode("a", [(b"a", b"b"), (b"a", b"b")])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate merges should be rejected")


if __name__ == "__main__":
    test()
