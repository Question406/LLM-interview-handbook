from collections import Counter


def bpe_one_merge(corpus, merges):
    """做一步 BPE 训练：合并最高频的相邻 pair，返回 (new_corpus, new_merges)。

    corpus: list[list[str]]，词尾已是 "endofword"；merges: 已发生的有序 merge 表。
    频次相同时选字典序较大的 pair；不修改输入。
    """
    pair_counts = Counter()
    for tokens in corpus:
        pair_counts.update(zip(tokens, tokens[1:]))
    if not pair_counts:
        return corpus, merges

    left, right = max(pair_counts, key=lambda pair: (pair_counts[pair], pair))
    merged = left + right
    new_corpus = []
    for tokens in corpus:
        index = 0
        output = []
        while index < len(tokens):
            if index + 1 < len(tokens) and tokens[index] == left and tokens[index + 1] == right:
                output.append(merged)
                index += 2  # 非重叠：跳过已合并的两个 token
            else:
                output.append(tokens[index])
                index += 1
        new_corpus.append(output)
    return new_corpus, list(merges) + [(left, right)]


# 重叠 pair：计数为 2，但只合并前两个；不修改输入
corpus = [["a", "a", "a"]]
merges = []
output, new_merges = bpe_one_merge(corpus, merges)
assert output == [["aa", "a"]]
assert new_merges == [("a", "a")]
assert corpus == [["a", "a", "a"]]
assert merges == []

# 没有任何相邻 pair：原样返回
output, new_merges = bpe_one_merge([["a"], ["b"]], [])
assert output == [["a"], ["b"]]
assert new_merges == []

# 频次相同时选字典序较大的 pair
output, new_merges = bpe_one_merge([["a", "b"], ["b", "c"]], [])
assert new_merges == [("b", "c")]
assert output == [["a", "b"], ["bc"]]

# 频次优先于字典序；pair 不跨列表统计
output, new_merges = bpe_one_merge([["x", "y"], ["x", "y"], ["y", "z"]], [])
assert new_merges == [("x", "y")]
assert output == [["xy"], ["xy"], ["y", "z"]]
output, new_merges = bpe_one_merge([["a", "b"], ["c", "d"]], [])
assert ("b", "c") not in new_merges

# 已有的 merge 表在末尾追加；四个 a 合成两个 aa
output, new_merges = bpe_one_merge([["a", "a", "a", "a", "endofword"]], [("q", "r")])
assert output == [["aa", "aa", "endofword"]]
assert new_merges == [("q", "r"), ("a", "a")]
