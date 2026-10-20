def tokenize(text):
    return set(text.lower().split())


def jaccard(left, right):
    union = left | right
    if not union:
        return 1.0  # 两个空集合视为完全相同
    return len(left & right) / len(union)


def dedup(stream, threshold=1.0):
    """流式去重：按出现顺序产出字符串，与已保留的某个代表的 Jaccard 相似度 >= threshold 就丢弃。

    只和已保留的代表比较；被丢弃的字符串不会成为新代表。
    """
    if not 0 < threshold <= 1:
        raise ValueError(f"threshold must be in (0, 1], got {threshold}")

    representatives = []
    for text in stream:
        tokens = tokenize(text)
        if any(jaccard(tokens, kept) >= threshold for kept in representatives):
            continue
        representatives.append(tokens)
        yield text


def test():
    def expect_value_error(fn, *args):
        try:
            list(fn(*args))
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # threshold = 1：词集合完全相同才算重复，忽略词序
    assert list(dedup(["a b", "b a", "a c"], 1)) == ["a b", "a c"]

    # 空白字符串的词集合都是空集，彼此相似度为 1
    assert list(dedup(["", "  ", "x"], 0.8)) == ["", "x"]

    # 相似关系不传递："a b" 被 "a" 挡掉，不能再拿它去挡 "b"
    assert list(dedup(["a", "a b", "b"], 0.5)) == ["a", "b"]

    # 大小写不敏感
    assert list(dedup(["Hello World", "hello world"])) == ["Hello World"]

    expect_value_error(dedup, ["a"], 0)
    expect_value_error(dedup, ["a"], 1.5)


if __name__ == "__main__":
    test()
