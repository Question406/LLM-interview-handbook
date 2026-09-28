---
id: coding-paged-table
section: coding
order: 26
level: A
title: 白板：PagedAttention 的 block table，逻辑页怎么映到物理块，append 一页
quick: >-
  KV 切成固定 $B_{\mathrm{s}}$ 个 token 的物理块。每条序列一张表：逻辑页号 $\to$ 物理块号。Cache 形状是
  `[P, H, B_s, D]`，不是连续 `[B, H, max_len, D]`。Append 时 `pos % B_s = 0` 才向空闲链表要一块。
tags:
  - Coding
  - PagedAttention
  - KV Cache
  - vLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
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

## 题怎么来的

vLLM 的 PagedAttention 把 OS 虚拟内存搬到 KV 上。NVIDIA serving / CUDA 白板会让你画 block
table，并手写「新 token 落到哪一页、页满了怎么 alloc」。系统账（碎片、前缀共享）见
`sys-paged-attn`、`nvidia-paged-kv`。本题落到可跑的索引：逻辑页、物理块、append 一页。注意力公式不变，变的是
$K,V$ 从哪读。

## 表、块、下标

物理块大小 $B_{\mathrm{s}}$（论文常用 $16$）。全局池 `k_cache`、`v_cache` 形状 `[P, H_{\mathrm{kv}}, B_{\mathrm{s}}, D]`，$P$ 是物理块个数。每条请求一份 `block_table`，形状 `[max_pages]`（batched 时 `[B, max_pages]`），dtype `int32`。逻辑页 $p=\lfloor \mathrm{pos}/B_{\mathrm{s}}\rfloor$，页内偏移 $o=\mathrm{pos}\bmod B_{\mathrm{s}}$，物理块号 $b=\mathrm{table}[p]$，则

$$
K[\mathrm{pos}]=k_{\mathrm{cache}}[b,:,o,:].
$$

按 max length 预留连续 `[B, H, L_{\max}, D]`
会同时制造内部空洞和外部碎片。分页之后内部碎片最多半块，外部碎片变成「空闲块链表」。GQA 只存 $H_{\mathrm{kv}}$ 组，不要把 table
建成 $H_q$ 份，见 `coding-gqa-repeat`。

Append 一条新 $k_t,v_t$（decode 一步，序列维是 $1$）：

1. 读当前长度 $\mathrm{pos}$（即将写入的下标）。
2. 若 $o=0$，从 free list 弹一块，写入 `table[p]`。
3. 把 $k_t$ 写进当前物理块的页内偏移，即 `cache[blk, :, off, :]`。
4. $\mathrm{pos}\leftarrow\mathrm{pos}+1$。

第一步 prefill 同样按 token 往页里填，只是一次写很多 $o$。不要在 $o\ne 0$ 时再
alloc，否则留下空洞页，gather 会读垃圾。

```python
import torch

class PagedKV:
    def __init__(self, n_blocks, n_heads, block_size, dim):
        self.bs = block_size
        self.k = torch.zeros(n_blocks, n_heads, block_size, dim)
        self.v = torch.zeros_like(self.k)
        self.free = list(range(n_blocks))

    def append_token(self, table, seq_lens, k_t, v_t):
        # table: [B, max_pages]; k_t,v_t: [B, H, 1, D]
        for b in range(k_t.size(0)):
            pos = int(seq_lens[b])
            page, off = divmod(pos, self.bs)
            if off == 0:
                table[b, page] = self.free.pop()
            blk = int(table[b, page])
            self.k[blk, :, off] = k_t[b, :, 0]
            self.v[blk, :, off] = v_t[b, :, 0]
            seq_lens[b] = pos + 1

    def gather_seq(self, table_row, seq_len):
        n = (seq_len + self.bs - 1) // self.bs
        blks = table_row[:n].long()
        h, d = self.k.size(1), self.k.size(-1)
        k = self.k[blks].transpose(0, 1).reshape(h, -1, d)[:, :seq_len]
        v = self.v[blks].transpose(0, 1).reshape(h, -1, d)[:, :seq_len]
        return k, v
```

`gather` 得到连续 `[H, S, D]` 只是为了对 kernel 形状；真 PagedAttention kernel 按 table 在片上
gather，不物化整段。白板先写对下标，再提 fused 路径。`free` 空了就是 KV 池 OOM，不是 `cat` 失败。

## 和注意力 kernel 的接口

Kernel 读的是 `(block_table, seq_lens, cache)`，不是 `(K_contig,
V_contig)`。Flash-Decoding 的 split 边界最好落在页边界上，否则一段 split 要跨两块物理页，见
`coding-flash-decode`。RoPE 在写入 cache 之前按绝对位置转完，页里存的是已经旋过的 $K$，见
`coding-rope-cache`。

前缀共享：多条请求指向同一物理块，refcount $>1$。Append 若要写一块共享页，先 copy-on-write 再改
table，不要原地覆盖别人的 prefix。投机拒绝是还页，不是 `cat` 再切片，见 `coding-spec-accept`。

逻辑页号对一条序列连续；物理块号来自空闲链表，可以不连续（虚拟地址 vs 物理页）。面试若问 kernel
怎么读：按 table 做间接 gather。先 `index_select` 拼成连续 `[H, S, D]` 再算注意力，会把分页的带宽优势吐回去；白板可以先 gather 对正确性，再补一句生产路径是 fused gather。

`seq_lens` 是权威长度。table 里多出来的 slot、最后一页没写满的行，都不能进 softmax。带着未初始化的 $0$
向量做注意力，等于多看了假 key。

## 追问

- **逻辑页和物理块谁是连续的？** 逻辑页号对一条序列是 $0,1,2,\ldots$；物理块号来自空闲链表，可以不连续。
- **为什么 `off==0` 才 alloc？** 页还没写满，下一 token 仍落在当前物理块。提前 alloc 浪费池子，还容易把 table 写成空洞。
- **`gather` 要不要把 pad 页算进去？** 只取 $\lceil S/B_{\mathrm{s}}\rceil$ 页，再用 $S$ 切掉最后一页多出来的 slot。带着未写满的垃圾做 softmax
  会吃到 $0$ 向量。
- **block size 太大或太小？** 太大内部碎片和 copy-on-write 变贵；太小 table 变长、kernel 间接寻址变多。16 是论文默认，是权衡不是定理。
