import numpy as np


class Sequence:
    """一个请求的页号表和逻辑长度。"""

    def __init__(self, pool, pages=(), length=0):
        self.pool = pool
        self.pages = list(pages)
        self.length = length
        self.closed = False


class PagePool:
    """引用计数的分页 KV 池；共享的未满尾页在写入时复制。"""

    def __init__(self, blocks, layers=2, heads=1, block_size=4, dim=2):
        if min(blocks, layers, heads, block_size, dim) < 1:
            raise ValueError("all pool dimensions must be positive")
        self.block_size = block_size
        self.storage = np.zeros((blocks, layers, 2, heads, block_size, dim))  # [P, L, 2, H_kv, B, d]
        self.refs = [0] * blocks
        self.free = list(range(blocks))

    def check(self, seq):
        if seq.pool is not self:
            raise ValueError("sequence belongs to a different pool")
        if seq.closed:
            raise ValueError("sequence was already released")

    def new(self):
        return Sequence(self)

    def fork(self, seq):
        """共享页表：每页引用数加 1，不复制 KV。"""
        self.check(seq)
        for block in seq.pages:
            self.refs[block] += 1
        return Sequence(self, seq.pages, seq.length)

    def allocate(self):
        if not self.free:
            raise MemoryError("KV pool exhausted")
        block = self.free.pop()
        assert self.refs[block] == 0, f"free block {block} still has references"
        self.refs[block] = 1
        self.storage[block].fill(0)
        return block

    def append(self, seq, token_kv):
        """追加一个 token 的全层 K/V，形状 [L, 2, H_kv, d]。OOM 时不改动任何状态。"""
        self.check(seq)
        token_kv = np.asarray(token_kv, dtype=float)
        expected = self.storage.shape[1:4] + self.storage.shape[-1:]
        if token_kv.shape != expected:
            raise ValueError(f"token_kv must have shape {expected}, got {token_kv.shape}")
        if not np.isfinite(token_kv).all():
            raise ValueError("token_kv contains non-finite values")

        offset = seq.length % self.block_size
        if offset == 0:
            block = self.allocate()  # 先分配，失败时页表不变
            seq.pages.append(block)
        else:
            block = seq.pages[-1]
            if self.refs[block] > 1:  # 共享的未满尾页：copy-on-write
                old = block
                block = self.allocate()  # OOM 时原引用数和页表都不变
                self.storage[block] = self.storage[old]
                self.refs[old] -= 1
                seq.pages[-1] = block
        self.storage[block, :, :, :, offset, :] = token_kv
        seq.length += 1

    def read(self, seq):
        """返回连续副本 [L, 2, H_kv, length, d]。"""
        self.check(seq)
        parts = [self.storage[block] for block in seq.pages]
        if not parts:
            shape = self.storage.shape[1:4] + (0, self.storage.shape[-1])
            return np.empty(shape)
        return np.concatenate(parts, axis=3)[:, :, :, :seq.length, :].copy()

    def release(self, seq):
        """每页引用数减 1，减到 0 才回到空闲列表。"""
        self.check(seq)
        for block in seq.pages:
            assert self.refs[block] > 0, f"block {block} released below zero"
            self.refs[block] -= 1
            if self.refs[block] == 0:
                self.free.append(block)
        seq.closed = True

    def validate(self, live_sequences):
        """检查引用数等于存活序列的持有数，空闲列表恰好是引用数为 0 的页。"""
        expected = [0] * len(self.refs)
        for seq in live_sequences:
            self.check(seq)
            pages_needed = (seq.length + self.block_size - 1) // self.block_size
            assert len(seq.pages) == pages_needed, "page table length does not match sequence length"
            for block in seq.pages:
                expected[block] += 1
        assert expected == self.refs, f"refcounts {self.refs} != expected {expected}"
        assert len(set(self.free)) == len(self.free), "free list has duplicates"
        unreferenced = {block for block, refs in enumerate(self.refs) if refs == 0}
        assert set(self.free) == unreferenced, "free list does not match unreferenced blocks"


# === TESTS ===
def token(value):
    return np.full((2, 2, 1, 2), float(value))  # [L, 2, H_kv, d]


def first_values(pool, seq):
    return pool.read(seq)[0, 0, 0, :, 0].tolist()


def expect_error(error, fn, *args):
    try:
        fn(*args)
    except error:
        return
    raise AssertionError(f"expected {error.__name__} from {fn.__name__}")


# fork 共享前缀页；各自追加时复制未满的共享尾页
pool = PagePool(4, block_size=4)
prefix = pool.new()
pool.append(prefix, token(1))
pool.append(prefix, token(2))
request_a = pool.fork(prefix)
request_b = pool.fork(prefix)
assert request_a.pages[0] == request_b.pages[0]
assert pool.refs[prefix.pages[0]] == 3

pool.append(request_a, token(3))
pool.append(request_b, token(9))
assert len({prefix.pages[0], request_a.pages[0], request_b.pages[0]}) == 3
assert first_values(pool, prefix) == [1, 2]
assert first_values(pool, request_a) == [1, 2, 3]
assert first_values(pool, request_b) == [1, 2, 9]
pool.validate([prefix, request_a, request_b])

# 全部释放后页都回到空闲列表；重复释放被拒绝
for seq in (request_b, prefix, request_a):
    pool.release(seq)
pool.validate([])
assert len(pool.free) == 4
expect_error(ValueError, pool.release, prefix)
expect_error(ValueError, pool.append, prefix, token(1))

# 共享的满页不需要 COW：追加时分配新的逻辑页
pool = PagePool(3, block_size=2)
a = pool.new()
pool.append(a, token(1))
pool.append(a, token(2))
b = pool.fork(a)
pool.append(b, token(3))
assert a.pages[0] == b.pages[0]
assert b.pages[1] != a.pages[0]
pool.validate([a, b])

# 没有空页做 COW：失败是原子的
pool = PagePool(1)
a = pool.new()
pool.append(a, token(4))
b = pool.fork(a)
pages_before = list(b.pages)
length_before = b.length
refs_before = list(pool.refs)
kv_before = pool.read(a)
expect_error(MemoryError, pool.append, b, token(5))
assert b.pages == pages_before
assert b.length == length_before
assert pool.refs == refs_before
assert np.array_equal(pool.read(a), kv_before)

# 释放 b 之后 a 独占这一页，可以原地追加
pool.release(b)
pool.append(a, token(6))
pool.validate([a])

# 跨池使用和形状错误
other = PagePool(1)
expect_error(ValueError, other.fork, a)
expect_error(ValueError, pool.append, a, np.zeros((1, 2, 1, 2)))

# 空序列读出长度为 0
assert pool.read(pool.new()).shape == (2, 2, 1, 0, 2)
