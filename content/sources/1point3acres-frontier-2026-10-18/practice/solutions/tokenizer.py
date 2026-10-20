END = object()  # trie 节点里标记「到这里是一个完整 token」的键


def build_trie(vocab, unk):
    """把词表建成字符 trie，完整 token 的节点在 END 键下存 token id。"""
    root = {}
    for word, token_id in vocab.items():
        if not word:
            raise ValueError("vocabulary must not contain the empty string")
        if token_id == unk:
            # 否则无法区分已知 token 和 unk，合并规则会出错
            raise ValueError(f"token id {token_id} collides with unk")
        node = root
        for char in word:
            node = node.setdefault(char, {})
        node[END] = token_id
    return root


def longest_match(trie, text, start):
    """从 start 起沿 trie 走，返回最长完整 token 的 (结束位置, id)；没有则 None。"""
    node = trie
    best = None
    position = start
    while position < len(text) and text[position] in node:
        node = node[text[position]]
        position += 1
        if END in node:
            best = (position, node[END])
    return best


def tokenize(text, vocab, unk=-1, merge_unk=True):
    """按 Unicode 字符做最长匹配分词；merge_unk 时连续未知字符只输出一个 unk。"""
    trie = build_trie(vocab, unk)
    output = []
    position = 0
    in_unknown_run = False
    while position < len(text):
        match = longest_match(trie, text, position)
        if match is None:
            if not (merge_unk and in_unknown_run):
                output.append(unk)
            position += 1  # 未知时恰好消耗一个字符，保证前进
            in_unknown_run = True
        else:
            position, token_id = match
            output.append(token_id)
            in_unknown_run = False
    return output


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    vocab = {"ab": 1, "a": 2}

    # 最长匹配，连续未知字符合并成一个 unk，已知 token 会打断合并
    assert tokenize("ab??a?", vocab) == [1, -1, 2, -1]

    # 关闭合并后，每个未知字符各输出一个 unk
    assert tokenize("ab??", vocab, merge_unk=False) == [1, -1, -1]

    # 空输入
    assert tokenize("", vocab) == []

    # 多字节字符按 Unicode 字符处理
    assert tokenize("你好?", {"你": 1, "你好": 2}) == [2, -1]

    # 走得最远的路径不一定是完整 token：要回退到最后一个完整 token
    assert tokenize("abc", {"a": 1, "abcd": 2}) == [1, -1]

    # 非法词表
    expect_value_error(tokenize, "a", {"": 1})
    expect_value_error(tokenize, "a", {"a": -1})


if __name__ == "__main__":
    test()
