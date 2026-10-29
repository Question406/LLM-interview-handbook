---
id: sys-paged-attn
section: systems
order: 6
level: S
title: 系统：PagedAttention 块表、复制、前缀共享
quick: >-
  PagedAttention 把 KV 分成固定 token 数的块，用 block table
  将连续的逻辑序列映射到可分散的物理页。按需分配和引用计数减少浪费，共享前缀在写入分叉时做 copy-on-write；attention 公式保持不变。
tags:
  - vLLM
  - NVIDIA
  - KV Cache
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: >-
      Efficient Memory Management for Large Language Model Serving with
      PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
  - title: 'vLLM — Easy, Fast, and Cheap LLM Serving with PagedAttention'
    url: 'https://vllm.ai/blog/2023-06-20-vllm'
    type: secondary
  - title: PagedAttention — Hugging Face TGI
    url: >-
      https://huggingface.co/docs/text-generation-inference/main/conceptual/paged_attention
    type: secondary
  - title: 'Paged Attention, IFB, and Request Scheduling — TensorRT-LLM'
    url: >-
      https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: secondary
---

vLLM 的 SOSP'23 论文中，PagedAttention 改的是 KV 的分配和寻址：把连续的逻辑序列映射到可以不连续的物理页，attention 计算本身保持不变。这样请求可以按实际长度增长，多条序列也能共享同一段前缀。

传统实现给每条请求预留 `max_len` 的连续 KV，实际回答短就浪费预留空间，空闲区零散又可能凑不出一整段。PagedAttention 把 KV 切成固定 token 数的 block，论文常用 16，每条序列用 block table 记录逻辑块号到物理块号。kernel 在 GPU 上查表、gather K/V，再算 $QK^{\top}$ 和加权 $V$，表本身远小于 KV。

生成写满一块再分配新页，请求结束释放页引用。只有缓存和其他请求都不再持有、引用数降到 0，页才回 free list。完整生命周期见 [[kv-prefix-paged-cow]]。这样 `sys-cont-batch` 才能在请求结束后补入新请求；单纯调高 `max_num_seqs`，解决不了连续预留导致的碎片和 OOM。

## 共享与代价

例如页大小 16 token、上下文 2k、实际只生成 200，连续预留可能浪费约 1800 token 的槽；分页主要浪费最后一页没填满的几格。八路并行 sampling 时，公共的 2k 前缀可以只占一份物理页，多条 block table 指向它，引用计数增加。分叉后若要写共享页，先 copy-on-write 复制成私有页再写，避免改坏其他序列。

并行 sampling、beam、多个用户共用 system prompt 都适合这种共享。跨请求该命中什么前缀，由 `sys-prefix-cache` 的缓存策略决定，CoW 则是底层的页共享机制。前缀不共享时也可以复制，但会多占几千 token 的物理空间。

页太小会增加表项和间接访问，妨碍 kernel 向量化与 L2 命中；页太大又增加块内碎片。常见大小是十几到几十 token，还要配合 kernel tile，改页大小需同步改 attention kernel。块表驻留 GPU，逐步往返 CPU 查表会增加延迟。

论文报告 naive 系统 KV 浪费可达百分之六十到八十，分页后接近只剩几个百分点的块内碎片，相对 Orca / FasterTransformer throughput 常见两到四倍，长序列更明显。收益主要来自同样 HBM 能容纳更多并发，decode 仍受内存带宽限制。TGI 使用 vLLM 的 CUDA kernel，TensorRT-LLM 自己实现 paged KV，使用同类寻址方式。

虚拟内存的类比适合解释映射和碎片，不宜延伸成磁盘 swap。PCIe 换页对 decode 太慢，分配失败通常采用抢占，把某条请求 KV 移到 CPU 或暂停；生产中一般避免频繁换出。FlashAttention 减少算子 HBM I/O，分页减少分配浪费，KV 量化减少每页字节，三者可叠加，例如页内放 FP8 KV、仍按表 gather。vLLM 也还包含 continuous batching 和调度，不能只用分页概括它。

## 追问

**它是近似 attention 吗？**
不是。$K/V$ 物理位置不同，按表取回后，数值应与连续 KV 一致。

**CoW 和 prefix cache 是同一层吗？**
不是。CoW 负责页级共享与分叉写入，prefix cache 决定跨请求命中条件。连续预留若为各 beam 各留最大长度，会重复占用公共前缀；分页让它们共享后再独立增长。

**它和操作系统缺页一样吗？**
主要相似在映射和碎片。KV 分配失败是抢占或拒绝分配，不能指望去磁盘取页维持正常 TPOT。

## 相关题

- [[nvidia-paged-kv]]：NVIDIA 问法 `nvidia-paged-kv`，讨论 block size 为 1 和抢页失败；也是前文 kernel 按表 gather 的实现细节。
- [[coding-paged-table]]：手写 block table 和 append。
- [[kv-prefix-paged-cow]]：refcount、CoW 和分配失败回滚。
- [[meta-vllm]]：合讲分页、continuous batching 与 GQA。
- [[sys-prefix-cache]]：跨请求的前缀命中条件。
- [[openai-continuous-batching]]：每步更换 batch 成员的调度。

相关实现：`openai-kv-cache-impl`。
