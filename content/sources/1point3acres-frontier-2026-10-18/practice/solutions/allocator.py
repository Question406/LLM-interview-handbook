import random


class Node:
    """treap 节点：一个空闲区间 [start, start + size)。按 start 排成 BST，按 priority 排成小根堆。"""

    def __init__(self, start, size, priority):
        self.start = start
        self.size = size
        self.priority = priority
        self.left = None
        self.right = None
        self.max_size = size  # 子树中最大的空闲区间长度


def max_size(node):
    return node.max_size if node else 0


def update(node):
    """子节点变化后重新计算 max_size。"""
    if node:
        node.max_size = max(node.size, max_size(node.left), max_size(node.right))
    return node


def split(node, key):
    """拆成 (start < key 的部分, start >= key 的部分)。"""
    if node is None:
        return None, None
    if node.start < key:
        node.right, right = split(node.right, key)
        return update(node), right
    left, node.left = split(node.left, key)
    return left, update(node)


def merge(left, right):
    """合并两棵 treap，要求 left 中所有 start 都小于 right 中的 start。"""
    if left is None:
        return right
    if right is None:
        return left
    if left.priority < right.priority:
        left.right = merge(left.right, right)
        return update(left)
    right.left = merge(left, right.left)
    return update(right)


def erase(node, key):
    """删除 start == key 的节点（调用方保证它存在）。"""
    if node.start == key:
        return merge(node.left, node.right)
    if key < node.start:
        node.left = erase(node.left, key)
    else:
        node.right = erase(node.right, key)
    return update(node)


class Allocator:
    """地址池 [0, capacity) 上的 first-fit 分配器。"""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self.rng = random.Random(3)  # 固定 seed，便于复现
        self.root = None
        self.allocated = {}  # 已分配块：起点 -> 长度
        self._insert_free(0, capacity)

    def _insert_free(self, start, size):
        left, right = split(self.root, start)
        node = Node(start, size, self.rng.random())
        self.root = merge(merge(left, node), right)

    def _first_fit(self, size):
        """返回起点最小、长度 >= size 的空闲节点；调用前已确认存在。"""
        node = self.root
        while True:
            if max_size(node.left) >= size:
                node = node.left  # 左子树地址更小，且里面有足够大的块
            elif node.size >= size:
                return node
            else:
                node = node.right

    def malloc(self, size):
        """分配 size 个单元，返回起点；没有足够大的连续空闲块时返回 None。"""
        if size < 1:
            raise ValueError(f"size must be positive, got {size}")
        if max_size(self.root) < size:
            return None
        block = self._first_fit(size)
        start, total = block.start, block.size
        self.root = erase(self.root, start)
        if total > size:
            self._insert_free(start + size, total - size)
        self.allocated[start] = size
        return start

    def _neighbors(self, ptr):
        """返回起点在 ptr 之前的最后一个空闲块，以及之后的第一个空闲块。"""
        before = after = None
        node = self.root
        while node:
            if node.start < ptr:
                before = node
                node = node.right
            else:
                after = node
                node = node.left
        return before, after

    def free(self, ptr):
        """释放 malloc 返回的块；ptr 非法或重复释放时返回 False。"""
        if ptr not in self.allocated:
            return False
        start = ptr
        size = self.allocated.pop(ptr)
        before, after = self._neighbors(ptr)
        if before and before.start + before.size == start:
            start = before.start
            size += before.size
            self.root = erase(self.root, before.start)
        if after and start + size == after.start:
            size += after.size
            self.root = erase(self.root, after.start)
        self._insert_free(start, size)
        return True


def test():
    # 基本分配、空间不足、释放后合并成整块
    allocator = Allocator(10)
    assert allocator.malloc(3) == 0
    assert allocator.malloc(4) == 3
    assert allocator.malloc(4) is None
    assert allocator.free(0)
    assert allocator.free(3)
    assert not allocator.free(3)  # 重复释放
    assert allocator.malloc(10) == 0

    # 和逐格扫描的 first-fit 朴素实现做随机对照
    rng = random.Random(8)
    capacity = 50
    allocator = Allocator(capacity)
    cells = [False] * capacity  # True 表示已占用
    live = {}
    for _ in range(1000):
        if live and rng.random() < 0.4:
            ptr = rng.choice(list(live))
            size = live.pop(ptr)
            assert allocator.free(ptr)
            cells[ptr:ptr + size] = [False] * size
        else:
            size = rng.randrange(1, 12)
            expected = next(
                (i for i in range(capacity - size + 1) if not any(cells[i:i + size])),
                None,
            )
            got = allocator.malloc(size)
            assert got == expected
            if got is not None:
                live[got] = size
                cells[got:got + size] = [True] * size


if __name__ == "__main__":
    test()
