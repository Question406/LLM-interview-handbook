class Node:
    def __init__(self, edge=(), values=(), parent=None):
        self.edge = tuple(edge)      # 这条边上的 token
        self.values = tuple(values)  # 每个 token 一个 KV 句柄
        self.parent = parent
        self.children = {}           # 子边首 token -> Node
        self.locks = 0               # 经过该节点的活跃 lease 数
        self.used = 0                # 最近访问的逻辑时钟


class RadixCache:
    """按 token 粒度压缩边的前缀树。值是不透明、不可变的 KV 句柄。"""

    def __init__(self):
        self.roots = {}
        self.clock = 0

    def root(self, namespace):
        return self.roots.setdefault(namespace, Node())

    def touch(self, node):
        self.clock += 1
        node.used = self.clock

    @staticmethod
    def split(child, length):
        """把 child 的边在 length 处拆成 mid -> child，返回新的中间节点 mid。"""
        if not 0 < length < len(child.edge):
            raise ValueError(f"split point {length} must be inside an edge of length {len(child.edge)}")
        parent = child.parent
        mid = Node(child.edge[:length], child.values[:length], parent)
        # 现存 lease 的终点对象不变、释放时会经过 mid，所以 mid 继承 child 的锁计数
        mid.locks = child.locks
        mid.used = child.used
        parent.children[mid.edge[0]] = mid
        child.edge = child.edge[length:]
        child.values = child.values[length:]
        child.parent = mid
        mid.children[child.edge[0]] = child
        return mid

    def walk(self, tokens, namespace, split_boundary=False):
        """沿树匹配 tokens，返回 (命中长度, 命中句柄, 终点节点)。

        split_boundary=True 时，命中点落在边中间就先拆边，让终点恰好是一个节点。
        """
        tokens = tuple(tokens)
        node = self.root(namespace)
        offset = 0
        values = []
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                break
            count = 0
            while (count < len(child.edge) and offset + count < len(tokens)
                   and child.edge[count] == tokens[offset + count]):
                count += 1
            values.extend(child.values[:count])
            offset += count
            if count < len(child.edge):
                if count and split_boundary:
                    node = self.split(child, count)
                break
            node = child
        return offset, tuple(values), node

    def match(self, tokens, namespace="default"):
        length, values, _ = self.walk(tokens, namespace)
        return length, values

    def insert(self, tokens, values, namespace="default"):
        """插入 tokens 及其句柄，返回已经在树里的前缀长度（调用方可丢弃这部分重复句柄）。"""
        tokens = tuple(tokens)
        values = tuple(values)
        if len(tokens) != len(values):
            raise ValueError(f"need one KV handle per token, got {len(tokens)} tokens and {len(values)} handles")
        node = self.root(namespace)
        offset = 0
        while offset < len(tokens):
            child = node.children.get(tokens[offset])
            if child is None:
                child = Node(tokens[offset:], values[offset:], node)
                node.children[child.edge[0]] = child
                self.touch(child)
                return offset
            count = 0
            while (count < len(child.edge) and offset + count < len(tokens)
                   and child.edge[count] == tokens[offset + count]):
                count += 1
            if count < len(child.edge):
                child = self.split(child, count)
            offset += count
            node = child
            self.touch(node)
        return offset

    def validate(self):
        """检查树结构不变量，返回树里的 token 总数。"""
        count = 0

        def visit(node):
            nonlocal count
            for first, child in node.children.items():
                assert child.parent is node and child.edge and first == child.edge[0]
                assert len(child.edge) == len(child.values)
                count += len(child.edge)
                visit(child)

        for root in self.roots.values():
            visit(root)
        return count


class PinnedRadix(RadixCache):
    """支持 lease 的 radix cache：活跃请求锁住整条祖先路径，淘汰只选未锁定的叶子。"""

    def __init__(self):
        super().__init__()
        self.leases = {}  # lease id -> 路径终点 Node
        self.next_lease = 0

    def acquire(self, tokens, namespace="default"):
        """锁住命中路径（必要时拆边），返回 (lease, 命中长度, 命中句柄)。"""
        length, values, node = self.walk(tokens, namespace, split_boundary=True)
        current = node
        while current.parent is not None:
            current.locks += 1
            self.touch(current)
            current = current.parent
        self.next_lease += 1
        self.leases[self.next_lease] = node
        return self.next_lease, length, values

    def release(self, lease):
        """沿终点当前的 parent 链把锁计数减回去。"""
        if lease not in self.leases:
            raise ValueError(f"unknown or already released lease: {lease!r}")
        current = self.leases.pop(lease)
        while current.parent is not None:
            assert current.locks > 0
            current.locks -= 1
            current = current.parent

    def evict(self, target_tokens):
        """按 LRU 移走未锁定的叶子，直到释放至少 target_tokens 个句柄或没有候选。"""
        if target_tokens < 0:
            raise ValueError(f"eviction target must be non-negative, got {target_tokens}")
        freed = []
        while len(freed) < target_tokens:
            candidates = []

            def visit(node):
                for child in node.children.values():
                    if not child.children and child.locks == 0:
                        candidates.append(child)
                    visit(child)

            for root in self.roots.values():
                visit(root)
            if not candidates:
                break
            victim = min(candidates, key=lambda candidate: candidate.used)
            del victim.parent.children[victim.edge[0]]
            freed.extend(victim.values)  # 一次移走整条边
        return tuple(freed)


# === TESTS ===
def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test():
    tree = PinnedRadix()
    tree.insert([1, 2, 3, 4], ["a", "b", "c", "d"])
    lease, length, values = tree.acquire([1, 2, 3, 4])
    assert length == 4
    assert values == ("a", "b", "c", "d")

    # 拆分一条已加锁的边：新的中间节点继承锁计数，受原 lease 保护
    tree.insert([1, 2, 9], ["a", "b", "x"])
    mid = tree.root("default").children[1]
    assert mid.locks == 1
    assert mid.children[3].locks == 1
    assert tree.evict(100) == ("x",)
    assert tree.match([1, 2, 3, 4])[0] == 4

    # 释放后锁计数归零，整条路径都可以被淘汰
    tree.release(lease)
    assert mid.locks == 0
    assert mid.children[3].locks == 0
    assert set(tree.evict(100)) == {"a", "b", "c", "d"}
    assert tree.validate() == 0

    # 重复释放报错
    expect_value_error(lambda: tree.release(lease))

    # 查询在边中间结束：只锁命中的前缀，不锁没用到的后缀
    tree.insert([5, 6, 7], ["e", "f", "g"])
    first, hit, _ = tree.acquire([5, 6])
    second, _, _ = tree.acquire([5, 6, 8])
    assert hit == 2
    assert tree.evict(100) == ("g",)

    # 重叠的 lease：释放一个后前缀仍被另一个保护
    tree.release(first)
    assert tree.evict(100) == ()
    tree.release(second)
    assert set(tree.evict(100)) == {"e", "f"}

    # LRU 由逻辑时钟决定：访问过 [1] 之后，先淘汰 [2]
    tree.insert([1], ["A"])
    tree.insert([2], ["B"])
    lease, _, _ = tree.acquire([1])
    tree.release(lease)
    assert tree.evict(1) == ("B",)

    # 目标为 0 不淘汰；目标为负、句柄数不对都报错
    assert tree.evict(0) == ()
    expect_value_error(lambda: tree.evict(-1))
    expect_value_error(lambda: tree.insert([3, 4], ["only-one"]))

    # 完全没命中的 acquire 不锁任何节点，释放也安全
    miss, hit, values = tree.acquire([42])
    assert hit == 0
    assert values == ()
    tree.release(miss)
    assert tree.evict(100) == ("A",)


if __name__ == "__main__":
    test()
