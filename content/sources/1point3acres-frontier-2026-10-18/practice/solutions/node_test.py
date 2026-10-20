def find_good_pair(n, test):
    """顺序测试所有二人组，返回第一个通过的 (i, j)；全部失败时返回 None。"""
    for i in range(n):
        for j in range(i + 1, n):
            if test([i, j]):
                return i, j
    return None


def bad_nodes(n, test):
    """返回坏节点集合；oracle 提供的信息不足以确定答案时返回 None。

    test(group) 只接受至少两个不同节点，当且仅当组内全是好节点时返回 True。
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    pair = find_good_pair(n, test)
    if pair is None:
        # 所有二人组都失败，说明好节点最多一个，而含有坏节点的组都会失败，
        # 「全坏」和「只有某一个好」这些情况给出的测试结果完全相同，无法区分
        return None

    partner = pair[0]  # 通过测试的组里两人都是好节点，任选一个当搭档
    bad = set()
    for node in range(n):
        if node in pair:
            continue
        # 搭档是好的，所以 [partner, node] 失败当且仅当 node 是坏的
        if not test([partner, node]):
            bad.add(node)
    return bad


def test():
    from itertools import product

    # 穷举 n = 2..6 的所有好坏组合
    for n in range(2, 7):
        for flags in product((False, True), repeat=n):
            bad = {node for node, is_bad in enumerate(flags) if is_bad}

            def oracle(group):
                assert len(group) >= 2
                assert len(set(group)) == len(group)
                return not any(node in bad for node in group)

            expected = bad if n - len(bad) >= 2 else None
            assert bad_nodes(n, oracle) == expected

    # 不到两个节点时没有合法测试，无法判定
    assert bad_nodes(0, lambda group: True) is None
    assert bad_nodes(1, lambda group: True) is None


if __name__ == "__main__":
    test()
