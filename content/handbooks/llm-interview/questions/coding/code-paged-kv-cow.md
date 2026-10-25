---
id: code-paged-kv-cow
section: coding
order: 215
level: S
title: 手写 Paged KV Cache 的 block table 与 copy-on-write（beam / 分支）
quick: "`fork` 只复制 block table，共享的物理页 refcount 各加 1。`append` 时如果末页 $\\mathrm{refcount}\\gt 1$，先复制这一页再写，免得改坏别的分支。"
tags:
  - KV Cache
  - Copy-on-Write
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: PagedAttention / vLLM
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

## 题目描述

实现分页 KV cache 的块管理元数据，支持序列分叉、追加一个 token 和释放。此练习只维护块编号与引用计数，不保存或复制实际 KV 张量。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `PagedKV(num_blocks,block_size)` 的 `fork(parent,child)`、`append(seq)`、`free_seq(seq)`。`num_blocks`/`block_size`为正；已有序列在 table 中记录块编号列表，used记录末块使用量。初始序列可用 `_new()` 获取块后设置 table[id]=[block]、used[id]=1。调用保证序列存在且空闲块足够，child尚不存在。

### 输出与约束

fork共享父序列已有块并增加引用计数；append占用一个新token槽，满末块时分配新块，共享且未满的末块要先独占再写；`free_seq`删除序列，引用数减为0的块回到free。不能修改其他共享序列的内容或长度。

### 示例

```text
num_blocks=3, block_size=2；建立一个占用1格的parent，fork为child，再append(child)
parent与child的末块编号应不同，used分别为1和2，两块引用计数各1。
释放两条序列后，3个块应全部回到空闲池。
```

## 解题思路与参考答案

`fork` 的时候只复制 block table，共享物理页的 refcount 各加 1；`append` 写新 token 时，如果末页还被别的序列共享，也就是 $\mathrm{refcount}\gt 1$，就先复制这一页再写。整段 $K,V$ 在 fork 时深拷贝一份是最常见的错法，PagedAttention 的收益恰好来自前缀共享物理页：beam、树采样、前缀缓存命中时，多条逻辑序列指向同一批 block，遇到写冲突才拆页。vLLM 论文把 KV 切成包含固定数量 token 的页，逻辑上连续、物理上可以散落，见 `sys-pagedattention`。注意力公式本身不变，见 `code-kv-cache-step`，这题只讨论分配器要守住的规则。

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

## 分支采样为什么必须 COW

Beam、树搜索、投机解码的多条候选共享同一个输入提示的前缀。如果每条候选独占一段连续的 KV，显存按宽度线性涨，paging 的共享就没了。COW 把共享停在「还没分叉的最后一页」：只读前缀的 `refcount` 可以很大，一旦某条序列要写新 token，只拆它自己的末页。Prefix cache 命中也是同一套不变量：缓存的物理页只读，新请求 `fork` 一份 table，用户 token 进来再拆。

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
够。解码只在尾部写。万一要随机写中间页（极少见），那一页同样要拆。Prefix cache 命中的是整段只读页。

**怎么和 `code-kv-cache-step` 接上？**
Attention 仍然用逻辑长度 $S$ 的 $K,V$，kernel 按 table 去 gather 物理页。手写一步可以用 `cat`，生产里用 paging。

**碎片怎么看？**
固定页有内部碎片，末页没写满；外部碎片比预留 `max_len` 的连续缓冲小得多。页太大内部浪费多，太小则 table 变大、间接访问变多。

**释放顺序和两条 beam 同时 append 要注意什么？**
子序列 `free_seq` 只减自己那份 ref，父序列的页不能提前回池，ref 算错就会出现悬空读写。两条 beam 同时 append 时，谁先写谁拆末页；后写的那条如果 `refcount` 还大于 1，也必须再 COW，不能假设 fork 之后末页还能一起写。漏拷贝物理字节的话，两条候选会读到错误的共享 HBM 数据，采样结果互相污染。
