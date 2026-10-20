from collections import Counter


def top_ngrams(documents, n, k):
    """统计所有文档里长度为 n 的 token 窗口，返回出现次数最多的 k 个。

    结果是 [(ngram_tuple, count), ...]，按次数降序，次数相同按 tuple 字典序升序。
    """
    if n < 1:
        raise ValueError(f"n must be at least 1: {n}")
    if k < 0:
        raise ValueError(f"k must be non-negative: {k}")
    counts = Counter()
    for tokens in documents:
        # 窗口只在单个文档内滑动，不跨文档拼接
        for start in range(len(tokens) - n + 1):
            counts[tuple(tokens[start:start + n])] += 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:k]


def test():
    # 重叠窗口分别计数，且不跨文档
    documents = [["a", "b", "a", "b"], ["a", "b"]]
    assert top_ngrams(documents, 2, 2) == [(("a", "b"), 3), (("b", "a"), 1)]

    # 文档比 n 短，没有任何窗口
    assert top_ngrams([["a"], ["b"]], 2, 5) == []

    # 次数相同按字典序
    assert top_ngrams([["b", "a"]], 1, 2) == [(("a",), 1), (("b",), 1)]

    # k = 0
    assert top_ngrams([["a"]], 1, 0) == []

    # 大小写不归一
    assert top_ngrams([["A", "a"]], 1, 5) == [(("A",), 1), (("a",), 1)]


if __name__ == "__main__":
    test()
