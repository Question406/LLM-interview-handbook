---
id: code-paged-kv-cow
section: coding
order: 215
level: S
title: 手写 Paged KV Cache 的 block table 与 copy-on-write（beam / 分支）
quick: "`fork` 只复制 block table，共享物理页的 refcount 各加 1。`append` 时如果末页 $\\mathrm{refcount}\\gt 1$，先复制这一页再写，免得改坏别的分支。"
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

常见误区是： `fork` 时把整段 $K,V$ 深拷贝一份。PagedAttention 的收益就是前缀共享物理页：beam / 树采样 / 前缀缓存命中时，多条逻辑序列指向同一批 block。写冲突才拆页。注意力公式不变，见 `code-kv-cache-step`；本题只讨论分配器需要保持的规则。vLLM 论文把 KV 切成包含固定数量 token 的页，逻辑连续、物理可散落，见 `sys-pagedattention`。

## 不变量

每条序列一份 `block_table: List[phys_id]`。物理页有 `refcount`。`fork(parent)` 复制 table，$O(\#\mathrm{blocks})$ 指针，每个 phys $+1$。`append` 只动最后一页：若该页 $\mathrm{refcount}\gt 1$ 或已满，分配新页（满则追加；共享则 COW 替换末页）。`free` 逐页 $-1$，到 0 回空闲链表。OOM 就是 `free` 空了；不要用悬空 phys id。

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

现场还需补上 `allocate`：根据序列长度向上取整，申请所需页数，`used` 记录最后一页已经写入的 token 数。上表省略物理 KV 数组；COW 时应对新页 `copy last block bytes`。面试官画 beam 宽度 2：共享前缀页 `ref=2`，第一条先进行逐 token 生成（decode）时，必须复制末页，第二条仍指向旧末页。

## 分支采样时为什么必须 COW

Beam、树搜索、投机解码的多条候选共享同一输入提示的前缀。若每条候选独占连续 KV，显存按宽度线性涨，paging 的共享就没了。COW 把共享停在「尚未分叉的最后一页」：只读前缀 `refcount` 可以很大；一旦某条序列要写新 token，只拆它自己的末页。Prefix cache 命中是同一套不变量：缓存的物理页只读，新请求 `fork` 一份 table，用户 token 到来再拆。

不要在 `fork` 时预分配到 `max_len`，那会重新造成大量内部碎片。OOM 时拒绝新 fork / append，不要覆盖别人的页。`allocate` 按 $\lceil T / B\rceil$ 向空闲链表要页，最后一页 $\mathrm{used}=T\bmod B$（整除则记 $B$）。物理 KV 可做成 `pages[phys, B, H, D]`，COW 时 `pages[nb] = pages[old].clone()` 再写新 token；手写可以只维护表与引用计数，但要口头补上拷贝字节，否则两条 beam 会写入同一块 HBM。和 `sys-pagedattention` 对照：那题讲虚拟内存类比；本题要维护 refcount，写路径只碰尾块。

## 追问

- **复杂度？** `fork` 是指针级 $O(\#\mathrm{blocks})$，不是 $O(T d)$。这才是 beam 能用 paging 的原因。
- **只 COW 末页够吗？** 解码只在尾部写。若随机写中间页（极少），那一页同样要拆。Prefix cache 命中的是整段只读页。
- **和 `code-kv-cache-step` 怎么接？** Attention 仍用逻辑长度 $S$ 的 $K,V$；kernel 按 table gather 物理页。手写一步可以用 `cat`，生产用 paging。
- **碎片？** 固定页有内部碎片（末页未满）；外部碎片远小于预留 `max_len` 连续缓冲。页太大内部浪费，太小则 table 与间接访问涨。
- **释放顺序？** 子序列 `free_seq` 只减自己那份 ref，父序列的页不能提前回池。ref 算错会产生悬空读写。
- **两条 beam 同时 append？** 谁先写谁拆末页；后写的那条若 `refcount` 仍大于 1，必须再 COW，不能假设 fork 之后末页还能一起写。漏拷贝物理字节时两条候选会访问错误的共享 HBM 数据，采样结果互相污染。
---
