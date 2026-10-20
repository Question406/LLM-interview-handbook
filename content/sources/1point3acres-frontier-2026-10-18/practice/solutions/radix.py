class Node:
    def __init__(self):
        self.is_key = False  # 只有终结节点代表一个完整的已存键
        self.edges = {}      # 首个 token -> (边标签 tuple, 子节点)


def common_prefix_length(a, b):
    length = 0
    while length < min(len(a), len(b)) and a[length] == b[length]:
        length += 1
    return length


class Radix:
    """整数序列的压缩前缀树：每条边的标签是一段非空 tuple。"""

    def __init__(self):
        self.root = Node()

    def insert(self, seq):
        rest = tuple(seq)
        node = self.root
        while rest:
            if rest[0] not in node.edges:
                leaf = Node()
                leaf.is_key = True
                node.edges[rest[0]] = (rest, leaf)
                return
            label, child = node.edges[rest[0]]
            shared = common_prefix_length(label, rest)
            if shared < len(label):
                # 只重合了一部分：拆成「公共前缀 -> 中间节点 -> 旧后缀」，旧键原样挂回
                middle = Node()
                middle.edges[label[shared]] = (label[shared:], child)
                node.edges[rest[0]] = (label[:shared], middle)
                child = middle
            node = child
            rest = rest[shared:]
        node.is_key = True  # 重复插入是幂等的

    def longest(self, seq):
        """返回 seq 的前缀中最长的已存键；一个都没有时返回 None。"""
        seq = tuple(seq)
        node = self.root
        pos = 0
        best = () if node.is_key else None
        while pos < len(seq) and seq[pos] in node.edges:
            label, child = node.edges[seq[pos]]
            if seq[pos:pos + len(label)] != label:
                break  # 停在边中间，不算命中
            pos += len(label)
            node = child
            if node.is_key:
                best = seq[:pos]
        return best

    def contains(self, seq):
        return self.longest(seq) == tuple(seq)

    def keys(self):
        """深度优先列出所有已存键。"""
        found = []

        def walk(node, prefix):
            if node.is_key:
                found.append(prefix)
            for label, child in node.edges.values():
                walk(child, prefix + label)

        walk(self.root, ())
        return found


def test():
    tree = Radix()
    for seq in ([1, 2, 3], [1, 2, 4], [1], []):
        tree.insert(seq)

    # [1, 2] 只是分裂出来的中间节点，不是已存键
    assert not tree.contains([1, 2])
    assert tree.contains([1])
    assert tree.contains([])

    # 最长前缀只在终结节点更新
    assert tree.longest([1, 2, 3, 9]) == (1, 2, 3)
    assert tree.longest([1, 2]) == (1,)
    assert tree.longest([1, 5]) == (1,)
    assert set(tree.keys()) == {(), (1,), (1, 2, 3), (1, 2, 4)}

    # 中间节点被补成键；重复插入不产生重复
    tree.insert([1, 2])
    tree.insert([1, 2])
    assert tree.contains([1, 2])
    assert sorted(tree.keys()) == [(), (1,), (1, 2), (1, 2, 3), (1, 2, 4)]

    # 没有空键时，无公共前缀返回 None
    assert Radix().longest([7]) is None


if __name__ == "__main__":
    test()
