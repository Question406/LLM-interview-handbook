---
id: coding-paged-table
section: coding
order: 26
level: A
title: 白板：PagedAttention 的 block table，逻辑页怎么映到物理块，append 一页
quick: "KV 池按每块 $B_{\\mathrm{s}}$ 个 token 分页，每条序列的表把逻辑页映到物理块。append 时先完成容量和缺页检查，只有 `pos % B_s == 0` 才申请新块，再写 KV 并增加长度，失败时保持原状态。"
tags:
  - 完整编程练习
  - Coding
  - PagedAttention
  - KV Cache
  - vLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: vLLM — Easy, Fast, and Cheap LLM Serving with PagedAttention
    url: https://blog.vllm.ai/2023/06/20/vllm.html
    type: secondary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: secondary
---

## 题目描述

实现分页 KV 缓存的简化页池与逻辑页表。每条序列独占物理页，追加 token 后应能按原序列顺序读回有效 K/V。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `PagedKV(n_blocks,n_heads,block_size,dim)` 初始化 K/V 池，形状 [`n_blocks`,H,`block_size`,D]，所有参数>=1，页初始空闲。
- `append_token(table,seq_lens,k_t,v_t)` 给 B 条序列各追加一个 token：table 为 [B,`max_pages`] 的页编号整数表，初始全 -1；`seq_lens` 为 [B] 初始全0；`k_t`/`v_t` 为 [B,H,1,D]。池、页表、长度原地更新，每条序列独占页，调用串行。
- `gather_seq(table_row,seq_len)` 返回按逻辑顺序排列的 (K,V)，各为 [H,`seq_len`,D]。`seq_len`=0 合法，返回空张量。
- 调用方保证表结构合法且每条序列有足够逻辑页槽。若物理空闲页不足，本次追加应抛 MemoryError，池、页表、长度和空闲页列表均保持原样；不要求形状非法校验。无需共享、释放或抢占。

### 输入输出示例

```text
block_size = 2, 一条序列依次追加 k = 1, 2, 3
-> 用了 2 个物理块：第一块存 [1, 2]，第二块存 [3, 空]
-> gather_seq(table[0], 3) 返回 k = [1, 2, 3]

池里只剩 1 个空闲块，两条空序列同时追加
-> 需要 2 块，MemoryError；table、seq_lens、空闲列表都保持原样
```

## 解题思路与参考答案

物理池按 `[P, H, B_s, D]` 存放块。append 先算逻辑页和页内偏移，再通过页表找到物理块；为了保证失败时状态不变，`append_token` 分成两阶段。第一阶段只读：对每条序列算出写入位置 `pos`、逻辑页 `page = pos // block_size` 和页内偏移 `offset = pos % block_size`，检查容量和现有页是否有效，并数出有多少条序列的 `offset == 0`、需要新块。第二阶段才提交：分配新块、写 K/V、长度加一。所有可能失败的检查都在第一阶段完成，所以出错时状态一点都没动。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题或官方测试。Python 3 + PyTorch，只在 CPU 浮点张量上验证，没测 GPU、多卡或性能。

### 题面、接口与约束

- `PagedKV(n_blocks, n_heads, block_size, dim)`：物理页池 `k`、`v`，形状都是 `[n_blocks, H, block_size, D]`，外加一个空闲块列表。任何一个参数小于 1 都抛 `ValueError`。
- `append_token(table, seq_lens, k_t, v_t)`：给 batch 里每条序列各追加一个 token。`table` 是 `[B, max_pages]` 的整数张量，初始全为 -1；`seq_lens` 是 `[B]`，初始全为 0；两者都原地更新。`k_t`、`v_t` 的形状是 `[B, H, 1, D]`。
- `gather_seq(table_row, seq_len) -> (k, v)`：按逻辑页顺序拼出一条序列的 K、V，形状 `[H, seq_len, D]`，只返回有效长度；`seq_len == 0` 合法，返回空张量。
- 每条序列独占自己的页，不考虑共享、释放和抢占；调用方串行调用。
- 原子性：token 形状不对、某条序列超出 `max_pages`、表里缺页时抛 `ValueError`；空闲块不够时抛 `MemoryError`。所有错误都必须在修改任何状态之前抛出。

### 输入输出示例

```text
block_size = 2, 一条序列依次追加 k = 1, 2, 3
-> 用了 2 个物理块：第一块存 [1, 2]，第二块存 [3, 空]
-> gather_seq(table[0], 3) 返回 k = [1, 2, 3]

池里只剩 1 个空闲块，两条空序列同时追加
-> 需要 2 块，MemoryError；table、seq_lens、空闲列表都保持原样
```

### 解题思路与正确性

只有 `offset == 0` 时才分配新块，其余情况下当前页还没写满，新 token 写进已有的块。

物理块号来自空闲列表，可以是任意顺序，不一定连续。`gather_seq` 按 `table_row` 里逻辑页的顺序取块，再在 `seq_len` 处截断，所以拿到的 K、V 顺序和写入顺序一致，最后一页没写满的 slot 也不会混进来。

### 完整参考实现（Python 3）

```python
import torch


class PagedKV:
    """分页 KV cache：物理页池 [n_blocks, H, block_size, D] + 每条序列一张逻辑页 -> 物理块的表。"""

    def __init__(self, n_blocks, n_heads, block_size, dim):
        if min(n_blocks, n_heads, block_size, dim) < 1:
            raise ValueError(
                f"all sizes must be >= 1, got n_blocks={n_blocks}, n_heads={n_heads}, "
                f"block_size={block_size}, dim={dim}"
            )
        self.block_size = block_size
        self.k = torch.zeros(n_blocks, n_heads, block_size, dim)
        self.v = torch.zeros_like(self.k)
        self.free = list(range(n_blocks))

    def append_token(self, table, seq_lens, k_t, v_t):
        """给每条序列追加一个 token。table: [B, max_pages]，seq_lens: [B]，k_t/v_t: [B, H, 1, D]。

        先检查完所有序列再提交，出错时 table、seq_lens 和空闲列表都不变。
        """
        batch = len(seq_lens)
        n_heads, dim = self.k.shape[1], self.k.shape[-1]
        expected = (batch, n_heads, 1, dim)
        if k_t.shape != expected or v_t.shape != expected:
            raise ValueError(f"k_t/v_t must have shape {expected}, got {tuple(k_t.shape)}, {tuple(v_t.shape)}")

        # 第一阶段：只读，规划每条序列写到哪一页、哪个偏移
        plan = []
        blocks_needed = 0
        for row in range(batch):
            pos = int(seq_lens[row])
            page, offset = divmod(pos, self.block_size)
            if pos < 0 or page >= table.shape[1]:
                raise ValueError(f"sequence {row} exceeds max_pages={table.shape[1]}")
            if offset == 0:
                blocks_needed += 1  # 当前页写满（或还没有页），需要一个新块
            else:
                block = int(table[row, page])
                if not 0 <= block < len(self.k):
                    raise ValueError(f"sequence {row} has no valid block for page {page}")
            plan.append((row, page, offset))
        if blocks_needed > len(self.free):
            raise MemoryError(f"need {blocks_needed} free KV blocks, only {len(self.free)} left")

        # 第二阶段：提交
        for row, page, offset in plan:
            if offset == 0:
                table[row, page] = self.free.pop()
            block = int(table[row, page])
            self.k[block, :, offset] = k_t[row, :, 0]
            self.v[block, :, offset] = v_t[row, :, 0]
            seq_lens[row] += 1

    def gather_seq(self, table_row, seq_len):
        """按逻辑页顺序拼出一条序列的 (k, v)，形状 [H, seq_len, D]。"""
        if seq_len < 0:
            raise ValueError(f"seq_len must be non-negative, got {seq_len}")
        n_heads, dim = self.k.shape[1], self.k.shape[-1]
        n_pages = (seq_len + self.block_size - 1) // self.block_size
        if n_pages > len(table_row):
            raise ValueError(f"seq_len={seq_len} needs {n_pages} pages, table has {len(table_row)}")
        blocks = table_row[:n_pages].long()
        if bool(((blocks < 0) | (blocks >= len(self.k))).any()):
            raise ValueError(f"page table has invalid block ids: {blocks.tolist()}")
        if seq_len == 0:
            return self.k.new_empty((n_heads, 0, dim)), self.v.new_empty((n_heads, 0, dim))
        # [pages, H, block_size, D] -> [H, pages, block_size, D] -> [H, pages * block_size, D]
        k = self.k[blocks].transpose(0, 1).reshape(n_heads, -1, dim)[:, :seq_len]
        v = self.v[blocks].transpose(0, 1).reshape(n_heads, -1, dim)[:, :seq_len]
        return k, v
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert k.flatten().tolist() == [1, 2, 3]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
torch.set_num_threads(1)


def expect_error(error_type, action):
    try:
        action()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def token(value, batch=1):
    return torch.full((batch, 1, 1, 1), float(value))


# 一条序列追加 3 个 token：用 2 个物理块，gather 按顺序取回
cache = PagedKV(4, 1, 2, 1)
table = torch.full((1, 3), -1)
lens = torch.zeros(1, dtype=torch.long)
for value in (1.0, 2.0, 3.0):
    cache.append_token(table, lens, token(value), token(value * 10))
k, v = cache.gather_seq(table[0], 3)
assert k.flatten().tolist() == [1, 2, 3]
assert v.flatten().tolist() == [10, 20, 30]
assert len(cache.free) == 2
assert table[0, 2] == -1

# 长度 0 合法，返回空张量
assert cache.gather_seq(table[0], 0)[0].shape == (1, 0, 1)

# 空闲块不够：MemoryError，所有状态不变
cache = PagedKV(1, 1, 2, 1)
table = torch.full((2, 1), -1)
lens = torch.zeros(2, dtype=torch.long)
expect_error(MemoryError, lambda: cache.append_token(table, lens, torch.ones(2, 1, 1, 1), torch.ones(2, 1, 1, 1)))
assert lens.tolist() == [0, 0]
assert torch.all(table == -1)
assert len(cache.free) == 1

# 两条序列交替追加：物理块号不连续，gather 仍按逻辑顺序拼接
cache = PagedKV(4, 1, 1, 1)
table = torch.full((2, 2), -1)
lens = torch.zeros(2, dtype=torch.long)
cache.append_token(table, lens, torch.tensor([1.0, 5.0]).view(2, 1, 1, 1), torch.zeros(2, 1, 1, 1))
cache.append_token(table, lens, torch.tensor([2.0, 6.0]).view(2, 1, 1, 1), torch.zeros(2, 1, 1, 1))
assert cache.gather_seq(table[0], 2)[0].flatten().tolist() == [1, 2]
assert cache.gather_seq(table[1], 2)[0].flatten().tolist() == [5, 6]
assert table.tolist() == [[3, 1], [2, 0]]  # 空闲列表从末尾弹出，每条序列拿到的块号不相邻

# 第二条序列超出 max_pages：ValueError，第一条序列也不会被写入
cache = PagedKV(2, 1, 2, 1)
table = torch.full((2, 1), -1)
lens = torch.tensor([0, 2])
expect_error(ValueError, lambda: cache.append_token(table, lens, token(9, 2), token(9, 2)))
assert lens.tolist() == [0, 2]
assert torch.all(table == -1)
assert len(cache.free) == 2

# token 形状不对、gather 越界、构造参数非法
cache = PagedKV(2, 2, 2, 3)
table = torch.full((1, 1), -1)
lens = torch.zeros(1, dtype=torch.long)
expect_error(ValueError, lambda: cache.append_token(table, lens, torch.ones(1, 1, 1, 3), torch.ones(1, 1, 1, 3)))
expect_error(ValueError, lambda: cache.gather_seq(table[0], 3))
expect_error(ValueError, lambda: cache.gather_seq(table[0], 1))
expect_error(ValueError, lambda: cache.gather_seq(table[0], -1))
expect_error(ValueError, lambda: PagedKV(0, 1, 1, 1))
```

### 复杂度与追问

设 batch 为 B、KV 头数 H、头维度 D。`append_token` 时间 O(B·H·D)，规划阶段额外空间 O(B)；`gather_seq` 时间和输出都是 O(H·seq_len·D)。

- 追问「生产系统还缺什么」：序列结束后的页回收、前缀共享用的引用计数和 copy-on-write、显存不够时的抢占。这些都不在本题「串行、独占页」的约定里，见下文。

## 题怎么来的

vLLM 的 PagedAttention 把操作系统的虚拟内存分页搬到了 KV cache 上。NVIDIA 的 serving / CUDA 白板会让你画 block table，并手写「新 token 落到哪一页、页满了怎么申请新块」。碎片、前缀共享这些系统层面的账见 `sys-paged-attn`、`nvidia-paged-kv`。本题只落到可运行的下标计算：逻辑页、物理块、append 一个 token。注意力公式本身不变，变的只是 $K,V$ 从哪里读。

## 表、块、下标

物理块大小记为 $B_{\mathrm{s}}$（论文常用 $16$）。全局池 `k_cache`、`v_cache` 的形状是 `[P, H_kv, B_s, D]`，$P$ 是物理块个数。每条请求一份 `block_table`，形状 `[max_pages]`（batch 时是 `[B, max_pages]`），dtype 是 `int32`。位置 $\mathrm{pos}$ 的逻辑页 $p=\lfloor \mathrm{pos}/B_{\mathrm{s}}\rfloor$，页内偏移 $o=\mathrm{pos}\bmod B_{\mathrm{s}}$，物理块号 $b=\mathrm{table}[p]$，于是

$$
K[\mathrm{pos}]=k_{\mathrm{cache}}[b,:,o,:].
$$

如果按最大长度给每条序列预留连续的 `[B, H, L_max, D]`，没用到的尾部是内部浪费，不同长度的请求之间还会产生外部碎片。分页之后，每条序列只有最后一页可能没写满，浪费不到一块（平均约半块）；外部碎片变成了空闲块列表里的可复用块。GQA 只存 $H_{\mathrm{kv}}$ 组 KV，不要把 table 或 cache 建成 $H_q$ 份，见 `coding-gqa-repeat`。

Append 一组新的 $k_t,v_t$（逐 token 生成（decode）的一步，序列维长度为 $1$）：

1. 读当前长度 $\mathrm{pos}$，也就是即将写入的下标。
2. 如果 $o=0$，从空闲列表弹出一块，写进 `table[p]`。
3. 把 $k_t$ 写进当前物理块的页内偏移处，即 `cache[blk, :, off, :]`。
4. $\mathrm{pos}\leftarrow\mathrm{pos}+1$。

第一步的输入预填充（prefill，即一次处理整段输入并建立缓存）也是按 token 往页里填，只是一次写很多个偏移。不要在 $o\ne 0$ 时申请新块，否则会留下没写满的空洞页，gather 时会读到垃圾数据。空闲列表空了，就是 KV 池 OOM，而不是某次 `cat` 失败。

## 和注意力 kernel 的接口

Kernel 的输入是 `(block_table, seq_lens, cache)`，不是连续的 `(K_contig, V_contig)`。练习里的 `gather_seq` 拼出连续的 `[H, S, D]`，只是为了对上普通注意力的输入形状、先验证正确性。真正的 PagedAttention kernel 按 table 在片上做间接 gather，不物化整段 K/V；如果先 `index_select` 拼成连续张量再算注意力，分页省下的带宽就又吐回去了。白板上先把下标写对，再补一句生产路径是 fused gather。

Flash-Decoding 的 split 边界最好落在页边界上，否则一段 split 要跨两个物理块，见 `coding-flash-decode`。RoPE 在写入 cache 之前就按绝对位置旋转好，页里存的是已经旋转过的 $K$，见 `coding-rope-cache`。

前缀共享时，多条请求指向同一个物理块，refcount $>1$。Append 时如果要写一块共享页，先 copy-on-write 复制一块、改 table，再写入，不能原地覆盖别人的前缀。投机解码被拒绝的 token 要把页还回去，而不是 `cat` 之后再切片，见 `coding-spec-accept`。

`seq_lens` 是权威长度。table 里多出来的 slot、最后一页没写满的行，都不能进 softmax；带着未初始化的 $0$ 向量做注意力，等于多看了几个假的 key。

## 追问

**逻辑页和物理块谁是连续的？**
逻辑页号对一条序列是 $0,1,2,\ldots$；物理块号来自空闲列表，可以不连续，就像虚拟地址和物理页的关系。
**为什么 `off == 0` 才申请新块？**
页还没写满时，下一个 token 仍然落在当前物理块里。提前申请会浪费池子，还容易在 table 里留下空洞。
**`gather` 要不要把 pad 页算进去？**
只取 $\lceil S/B_{\mathrm{s}}\rceil$ 页，再按 $S$ 切掉最后一页多出来的 slot。
**block size 太大或太小会怎样？**
太大时，最后一页的浪费和 copy-on-write 的复制成本都会变大；太小时，table 变长，kernel 的间接寻址次数变多。16 是论文的默认值，是权衡的结果，不是定理。

## 相关题

- [[sys-paged-attn]]：同一机制的口述版，多讲 copy-on-write 和前缀共享，不写代码。
- [[nvidia-paged-kv]]：NVIDIA 问法的口述版，侧重碎片从哪来、block size 取舍和抢页失败怎么办。
- [[kv-prefix-paged-cow]]：在这张页表上再加引用计数和写时复制，并要求分配失败时页表不变。
- [[meta-vllm]]：Meta 问法，讲 vLLM 为什么 GQA 之后还要分页，以及分页怎么配合 continuous batching。
