def flatten(node):
    """按深度优先顺序返回所有整数叶子。dict 按插入顺序遍历 value。"""
    leaves = []
    _collect_leaves(node, leaves)
    return leaves


def _collect_leaves(node, leaves):
    # 所有层共用一个 leaves 列表，每个叶子只追加一次，总时间 O(n)
    if type(node) is int:  # bool 是 int 的子类，这里故意排除
        leaves.append(node)
        return
    if isinstance(node, dict):
        if not all(isinstance(key, str) for key in node):
            raise ValueError("dict keys must be str")
        children = node.values()
    elif isinstance(node, (list, tuple)):
        children = node
    else:
        raise ValueError(f"unsupported leaf: {node!r}")
    for child in children:
        _collect_leaves(child, leaves)


def unflatten(template, values):
    """按 template 的结构依次填入 values，返回新对象，不修改 template。"""
    remaining = iter(values)

    def rebuild(node):
        if type(node) is int:
            try:
                value = next(remaining)
            except StopIteration:
                raise ValueError("too few values") from None
            if type(value) is not int:
                raise ValueError(f"value must be int: {value!r}")
            return value
        if isinstance(node, dict):
            return {key: rebuild(child) for key, child in node.items()}
        if isinstance(node, list):
            return [rebuild(child) for child in node]
        if isinstance(node, tuple):
            return tuple(rebuild(child) for child in node)
        raise ValueError(f"unsupported template node: {node!r}")

    result = rebuild(template)
    leftover = object()
    if next(remaining, leftover) is not leftover:
        raise ValueError("too many values")
    return result


class Iterator:
    """遍历嵌套结构的整数叶子；状态是「下一个要返回的叶子下标」。"""

    def __init__(self, data):
        self.leaves = flatten(data)
        self.pos = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos == len(self.leaves):
            raise StopIteration
        value = self.leaves[self.pos]
        self.pos += 1
        return value

    def get_state(self):
        return self.pos

    def set_state(self, pos):
        if type(pos) is not int or not 0 <= pos <= len(self.leaves):
            raise ValueError(f"invalid state: {pos!r}")
        self.pos = pos


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    data = [1, (), {"a": [2, 3]}]
    assert flatten(data) == [1, 2, 3]
    assert unflatten(data, [7, 8, 9]) == [7, (), {"a": [8, 9]}]

    # 保存状态后继续迭代，再恢复，应能重放同一段
    it = Iterator(data)
    assert next(it) == 1
    state = it.get_state()
    assert list(it) == [2, 3]
    it.set_state(state)
    assert list(it) == [2, 3]

    expect_value_error(unflatten, data, [1])           # 值不够
    expect_value_error(unflatten, data, [1, 2, 3, 4])  # 值多了
    expect_value_error(flatten, [True])                # bool 不算整数叶子
    expect_value_error(it.set_state, 4)                # 超出叶子数
    assert list(Iterator([[], (), {}])) == []


if __name__ == "__main__":
    test()
