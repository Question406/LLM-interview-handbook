---
id: kv-prefix-paged-cow
section: systems
order: 34
level: S
title: "KV Prefix ④：共享 KV 页的引用计数与 Copy-on-Write"
quick: "多个请求共享同一物理前缀页；只有写共享的未满尾页才复制，尾页已满就直接分配新页；分配失败时页表和引用数保持不变。"
tags:
  - 完整编程练习
  - KV Prefix 实现专题
  - Coding
  - KV Cache
  - Radix Tree
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "vLLM prefix caching allocation and reference counts"
    url: https://docs.vllm.ai/en/latest/design/prefix_caching/
    type: primary
  - title: "PagedAttention paper"
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

## 完整编程练习（手册原创实现版）

> 这是为理解开源机制而写的独立练习，不是某家公司的已确认原题，也不是 SGLang / vLLM 源码的逐字翻译。接口、简化条件和测试由手册定义。Python 3 + NumPy，在 CPU 上测试数值和状态语义，不报告 GPU 吞吐。

专题入口：[[kv-prefix-implementation-index]]。

### 题面、接口与约束

- `PagePool(blocks, layers, heads, block_size, dim)`：物理页池。一个物理页保存所有层的 K/V，`storage` 形状是 `[P, L, 2, H_kv, B, d]`（$P$ 页，$L$ 层，K/V 两份，$H_{kv}$ 个 KV head，每页 $B$ 个 token，头维 $d$）。
- `new() -> Sequence`：空序列。`Sequence` 保存页号表 `pages` 和逻辑长度 `length`。
- `fork(seq) -> Sequence`：只复制页表，并给每一页的引用数加 1，不复制 KV。
- `append(seq, token_kv)`：追加一个 token，`token_kv` 形状 `[L, 2, H_kv, d]`。如果尾页未满且被共享，先复制（copy-on-write）再写；如果尾页已满，直接分配一个新页，原来的满页继续共享。
- `read(seq)`：返回该序列的连续 KV 副本，形状 `[L, 2, H_kv, length, d]`。
- `release(seq)`：给每页引用数减 1，只有减到 0 才把页放回空闲列表。同一序列不能释放两次，也不能拿到别的池里用。
- `validate(live_sequences)`：检查引用数、页表长度和空闲列表是否一致。
- 页池不够时抛 `MemoryError`，并且序列长度、页表和引用数都保持不变。所有操作串行执行。

### 输入输出示例

```text
block_size = 4，前缀 [1, 2] fork 成 A、B
A.append(3)，B.append(9)
read(prefix) -> [1, 2]
read(A)      -> [1, 2, 3]
read(B)      -> [1, 2, 9]
如果前缀正好填满一页，A 追加时不会复制那一页，而是分配一个新页
```

### 解题思路与正确性

逻辑长度决定哪些 token 有效。页的引用数统计的是所有还活着的持有者，生产系统里缓存索引自己也算一个。

COW 的顺序很重要：先分配新页，成功后再给旧页减引用、改请求的页表。这样分配失败时什么都没改，`MemoryError` 之后状态和调用前完全一样。尾页已满时也一样，先分配再把新页号加进页表。

复制和写入都针对整页的全部层和 K/V 两份，避免只保护了一层，或者只复制了 K 漏掉 V。

### 完整参考实现（Python 3）

```python
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
```

### 可执行测试

```python
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
```

### 复杂度与追问

记 $N_{\text{pages}}$ 为序列的页数，$L$、$H_{kv}$、$B$、$d$ 同上，$P$ 为物理页数。`fork` 是 $O(N_{\text{pages}})$，只动页表。普通 `append` 写一个 token 的全层 KV，即 $O(LH_{kv}d)$；COW 时额外复制一整页，$O(LH_{kv}Bd)$。`release` 是 $O(N_{\text{pages}})$。持久的物理存储是 $O(PLH_{kv}Bd)$。`read` 返回的是给测试用的连续副本，生产里的 attention 直接按页表读，不需要这次拷贝。

- 追问「请求结束时能直接 free 吗」：不能。缓存索引作为持有者也要占一份引用，请求结束只减自己那一份；否则还在缓存里的前缀会被别的请求覆盖。
- 追问「多线程怎么办」：引用检查、分配和写入必须作为一个整体加锁或用其他方式同步。本题假设串行，并不自动保证线程安全。

## 相关题

- [[kv-prefix-implementation-index]]：专题入口。
- [[coding-paged-table]]：只做页表映射和 append 的白板题，没有引用计数和 COW。
- [[sys-paged-attn]]：口述版，讲前缀共享为什么要靠 CoW、写时再拆页。
- [[nvidia-paged-kv]]：NVIDIA 问法的口述版，含 refcount 共享和抢页失败。
- [[kv-prefix-radix-leases]]：第③题，树上的 lease 计数，和这里的物理页 refcount 不是同一个量。
- [[kv-prefix-engine]]：第⑧题，把它的连续 cache 换成本题的页池是扩展作业。
