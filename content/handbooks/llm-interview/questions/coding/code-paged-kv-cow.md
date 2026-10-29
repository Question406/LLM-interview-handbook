---
id: code-paged-kv-cow
section: coding
order: 215
level: S
title: 手写 Paged KV Cache 的 block table 与 copy-on-write（beam / 分支）
quick: >-
  `fork` 只复制 block table，共享的物理页 refcount 各加 1。`append` 时如果末页
  $\mathrm{refcount}\gt 1$，先复制这一页再写，免得改坏别的分支。
tags:
  - KV Cache
  - Copy-on-Write
  - Coding
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: PagedAttention / vLLM
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
---

## 题目描述

实现一个分页 KV cache 的**元数据管理器**。多条逻辑序列可以共享物理 block；某条序列要向共享尾 block 追加 token 时，需要为它分配独立 block，避免影响其他序列。本题只管理 block IDs、使用量与引用计数，不存储或复制真实 K/V tensors。

以下类、可检查属性和 allocation 规则为手册练习约定，不要求实现 vLLM。输入保证合法，不要求并发或完整 OOM recovery。

### 类与状态

实现 `PagedKV(num_blocks,block_size)`，两项均为正整数。构造后必须提供：

- `bs=block_size`；`free=list(range(num_blocks))`，表示空闲物理 block IDs。
- `ref=[0]*num_blocks`，`ref[b]` 是当前引用 block b 的逻辑序列数。
- `table={}`，保存 `sequence_id -> block ID list`。
- `used={}`，保存每条序列末 block 的 token 使用量，范围 `[1,bs]`。

一条序列除末 block 外的 blocks 都已写满。Sequence ID 为可哈希值，题目操作中不会改变其内容。

### 必须实现的接口

| 方法 | 行为与返回值 |
| --- | --- |
| `_new()` | 从 free 的末尾 pop 一个 block，设对应 ref 为 1，并返回 block ID；没有空闲 block 时抛 MemoryError |
| `fork(parent,child)` | child 获得 parent 的 block ID list 的独立副本和相同 used；所有共享 blocks 的 ref 各加 1；返回 None |
| `append(seq)` | 为 seq 增加一个 token 的逻辑空间；按下方规则更新，返回 None |
| `free_seq(seq)` | 删除该序列的 table、used；各 block ref 减 1，减为 0 时 append 回 free；返回 None |

`fork` 的 child 尚不存在，parent / seq 均已存在。除独立测试 `_new()` 的 OOM 情况外，保证操作所需的空闲 blocks 足够。

本题不要求额外的 create 方法。测试会通过 `_new()` 创建一个已有 1 个 token 的序列，例如：`b=cache._new(); cache.table['p']=[b]; cache.used['p']=1`。也可给定满足不变量的多 block 初态。

### append 的三种情况

1. 末 block 已满：申请新 block，追加到本序列的 table，令 used=1；旧 blocks 的 ref 不变。
2. 末 block 未满且 ref>1：申请新 block，将本序列的末 block ID 替换为新 ID，旧 block ref 减 1，used 加 1。这一步只模拟 copy-on-write 的元数据更新。
3. 末 block 未满且 ref=1：直接将本序列 used 加 1。

其他序列的 table 和 used 均不得改变。`fork` 不能预先为 child 分配所有新 blocks；对任何仍在使用的 block 不能提前回收。

### 完整操作示例

```text
cache=PagedKV(num_blocks=3,block_size=2)
b=cache._new()  # b=2
cache.table['p']=[b]; cache.used['p']=1
cache.fork('p','c')
此时 table={'p':[2],'c':[2]}, used={'p':1,'c':1}, ref=[0,0,2], free=[0,1]

cache.append('c')
此时 table={'p':[2],'c':[1]}, used={'p':1,'c':2}, ref=[0,1,1], free=[0]

cache.free_seq('c'); cache.free_seq('p')
此时 table={}, used={}, ref=[0,0,0], free=[0,1,2]
```

## 解题思路与参考答案

`fork` 的时候只复制 block table，共享物理页的 refcount 各加 1；`append` 写新 token 时，如果末页还被别的序列共享，也就是 $\mathrm{refcount}\gt 1$，就先复制这一页再写。整段 $K,V$ 在 fork 时深拷贝一份是最常见的错法，PagedAttention 的收益恰好来自前缀共享物理页：beam、树 sampling、前缀缓存命中时，多条逻辑序列指向同一批 block，遇到写冲突才拆页。vLLM 论文把 KV 切成包含固定数量 token 的页，逻辑上连续、物理上可以散落，见 `sys-pagedattention`。attention 公式本身不变，见 `code-kv-cache-step`，这题只讨论分配器要守住的规则。

## 不变量

每条序列有一份 `block_table: List[phys_id]`，每个物理页有一个 `refcount`。`fork(parent)` 复制 table，代价是 $O(\#\mathrm{blocks})$ 个指针，每个 phys 加 1。`append` 只动最后一页：这一页已满就追加新页；$\mathrm{refcount}\gt 1$ 就 COW，换一个新页替掉末页。`free` 逐页减 1，减到 0 就回空闲链表。OOM 就是 `free` 空了，这时别去用悬空的 phys id。

```python
class PagedKV:
    def __init__(self, num_blocks, block_size):
        self.bs = block_size
        self.free = list(range(num_blocks))
        self.ref = [0] * num_blocks
        self.table = {}
        self.used = {}  # last-block fill 1..bs

    def _new(self):
        if not self.free:
            raise MemoryError("kv oom")
        b = self.free.pop()
        self.ref[b] = 1
        return b

    def fork(self, parent, child):
        self.table[child] = list(self.table[parent])
        self.used[child] = self.used[parent]
        for b in self.table[child]:
            self.ref[b] += 1

    def append(self, seq):
        blocks, u = self.table[seq], self.used[seq]
        last = blocks[-1]
        if u == self.bs:
            blocks.append(self._new())
            self.used[seq] = 1
        elif self.ref[last] > 1:
            nb = self._new()
            self.ref[last] -= 1
            blocks[-1] = nb
            self.used[seq] = u + 1
        else:
            self.used[seq] = u + 1

    def free_seq(self, seq):
        for b in self.table.pop(seq):
            self.ref[b] -= 1
            if self.ref[b] == 0:
                self.free.append(b)
        del self.used[seq]
```

现场还要补一个 `allocate`：按序列长度向上取整申请页数，即 $\lceil T / B\rceil$ 页，`used` 记录最后一页已经写了多少 token，$\mathrm{used}=T\bmod B$，整除时记 $B$。上面的代码省略了物理 KV 数组。物理 KV 可以做成 `pages[phys, B, H, D]`，COW 时 `pages[nb] = pages[old].clone()` 再写新 token。手写时可以只维护表和引用计数，但要口头补上 COW 时对新页 `copy last block bytes` 这一步，否则两条 beam 会写进同一块 HBM。

面试官常画 beam 宽度 2 的情况：共享的前缀页 `ref=2`，第一条序列先做 decode 时必须复制末页，第二条仍然指向旧的末页。

## 分支 sampling 为什么必须 COW

Beam、树搜索、speculative decoding 的多条候选共享同一个 prompt 的前缀。如果每条候选独占一段连续的 KV，显存按宽度线性涨，paging 的共享就没了。COW 把共享停在「还没分叉的最后一页」：只读前缀的 `refcount` 可以很大，一旦某条序列要写新 token，只拆它自己的末页。Prefix cache 命中也是同一套不变量：缓存的物理页只读，新请求 `fork` 一份 table，用户 token 进来再拆。

所以 `fork` 时别预分配到 `max_len`，那样又会造成大量内部碎片。OOM 时拒绝新的 fork 或 append，绝不覆盖别人的页。和 `sys-pagedattention` 对照着看：那题讲虚拟内存类比，这题要把 refcount 维护对，写路径只碰尾块。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

先建立只有一个 token 的父序列，再 fork。给子序列追加时应复制共享的尾块，父序列不变；最后释放两条序列，所有块都应回到空闲表。该示例检查分配元数据，尚未模拟 KV 数据的物理复制。

```python
cache = PagedKV(num_blocks=3, block_size=2)
block = cache._new()
cache.table["parent"] = [block]
cache.used["parent"] = 1
cache.fork("parent", "child")
assert cache.ref[block] == 2
cache.append("child")
assert cache.table["parent"] == [block]
assert cache.table["child"] != [block]
assert cache.used["parent"] == 1 and cache.used["child"] == 2
cache.free_seq("child")
cache.free_seq("parent")
assert len(cache.free) == 3 and cache.ref == [0, 0, 0]
print("simple tests passed")
```

## 追问

**fork 的复杂度是多少？**
指针级的 $O(\#\mathrm{blocks})$，和 $O(T d)$ 的深拷贝差得很远。beam 能用 paging 就靠这一点。

**只 COW 末页够吗？**
够。decoding 只在尾部写。万一要随机写中间页（极少见），那一页同样要拆。Prefix cache 命中的是整段只读页。

**怎么和 `code-kv-cache-step` 接上？**
Attention 仍然用逻辑长度 $S$ 的 $K,V$，kernel 按 table 去 gather 物理页。手写一步可以用 `cat`，生产里用 paging。

**碎片怎么看？**
固定页有内部碎片，末页没写满；外部碎片比预留 `max_len` 的连续缓冲小得多。页太大内部浪费多，太小则 table 变大、间接访问变多。

**释放顺序和两条 beam 同时 append 要注意什么？**
子序列 `free_seq` 只减自己那份 ref，父序列的页不能提前回池，ref 算错就会出现悬空读写。两条 beam 同时 append 时，谁先写谁拆末页；后写的那条如果 `refcount` 还大于 1，也必须再 COW，不能假设 fork 之后末页还能一起写。漏拷贝物理字节的话，两条候选会读到错误的共享 HBM 数据，sampling 结果互相污染。
