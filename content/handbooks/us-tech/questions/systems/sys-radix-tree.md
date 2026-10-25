---
id: sys-radix-tree
section: systems
order: 25
level: A
title: 系统：radix / prefix tree 共享 KV（SGLang）
quick: "RadixAttention 用 CPU 上的压缩前缀树查最长公共 token 前缀，把命中的 GPU KV 页挂到请求的 block table，只重算后缀。共享页写入前做 CoW，淘汰优先处理无引用的叶子，同时保留安全边界与在途请求的显存预算。"
tags:
  - SGLang
  - vLLM
  - KV Cache
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Fast and Expressive LLM Inference with RadixAttention and SGLang
    url: https://lmsys.org/blog/2024-01-17-sglang/
    type: primary
  - title: SGLang — Efficient Execution of Structured Language Model Programs
    url: https://arxiv.org/abs/2312.07104
    type: primary
  - title: Automatic Prefix Caching — vLLM
    url: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
    type: secondary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

RadixAttention 用一棵压缩前缀树找请求能复用的最长 KV 前缀，只对后缀做 prefill。例如多轮对话前两轮相同、第三轮才分叉，树就把公共路径留下，各自接新的分支。它是 SGLang 公开的索引设计，LMSYS 2024 博客和 SGLang 论文都有说明。

树维护在 CPU，KV 页仍在 GPU。树边标记一段 token，比逐 token trie 更浅，节点记录引用计数与 GPU 物理页下标；博客指出，相对 GEMM，这部分 CPU 开销可忽略。$page_size \gt 1$ 时还要把命中长度对齐页边界，不足一页的尾部当 miss 重算。

请求带完整 prompt 到运行时，由运行时从根找最长驻留前缀，再把命中页写进该请求的 block table。多条请求引用同一页，不用 memcpy。开始生成后若要写已共享的页，必须 copy-on-write，避免改变其他请求的前缀。查询要逐边比较最长公共段，即使在压缩边中途分歧，也返回已经命中的部分，并累积沿途所有 KV 句柄，不能只取末节点 payload。

相比 vLLM 块哈希，树更直接表达部分共享和分叉，如相同工具 schema 后接不同参数、agent 多轮、并行采样和 beam；块哈希适合逐块完全一致的匹配。两者都能复用前缀，性能还取决于命中粒度、索引成本与生命周期策略，不能只凭名字判断。SGLang 的 `extra_key` 还把 LoRA、adapter 和不应共享的命名空间分开，token 一样也不一定能共用路径。通用命中条件见 `sys-prefix-cache`。

## 淘汰与调度

HBM 有限，公开策略用 LRU 并优先淘汰叶子，尽量不拆共享主干。根附近的系统提示命中频繁，一小时前某条对话的私有尾巴可先淘汰；随意移除中间节点会让子树失去有效路径。页级引用与实际使用状态必须一起维护。

Cache-aware 调度可把共享前缀请求排在一起，增加命中，也有利于 FlashInfer cascade 的公共 KV 加私有 KV 计算，见 `sys-flashinfer`。只追瞬时 tokens/s、任意打乱请求，可能使主干引用计数频繁变动。请求结束后也别立刻丢掉生成段，把它插回树，下一轮才能复用“系统提示 + 上轮问答”，见 `sys-agent-sched`。

Radix 是索引，PagedAttention 是物理页管理，kernel 仍按 block table 读页，不会逐步在 GPU 遍历 CPU 树，也没改注意力公式，数值应与按页 gather 的精确注意力一致。分页方便分配和分叉，但共享在数学上不依赖分页；连续只读 prefix 与私有 suffix 也能做分段 attention，见 [[kv-prefix-segmented-attention]]。分页的原语见 `sys-paged-attn`，两层配合可以零拷贝挂接共享页。

热门主干也可能占满 KV 池，让命中率上升、P99 TPOT 变差，需要限制单前缀比例，和在途 decode 分池或设水位。跨机副本没有同一棵树，要做亲和路由或接受 miss。公共系统提示可共享，用户文档默认不跨租户复用。

## 追问

**树和块哈希怎么选？**
大量部分共享、多轮分叉时考虑树；几乎只有完全相同的系统提示、分叉少时，块哈希就够。

**一个空格变化会怎样？**
从第一个不同 token 断开。仍整段命中，要查 token ID 与 template 版本是否进 key。

**页大小影响什么？**
页大时短分叉也要重算一截，页小时索引更细、树更深，kernel 间接访问更多。

**为什么保留生成结果？**
下一轮 prompt 会包含旧回答。不插入生成段，下一轮就得从原分叉处重新 prefill。

**LoRA 能共享主干吗？**
通常不能，`extra_key` 必须区分，否则会出现不易发现的错命中。

## 相关题

- [[kv-prefix-implementation-index]]：8 道题覆盖每层 Transformer KV、树分裂、lease 与淘汰、分页 COW、块哈希、分段 attention、命中规划和端到端复用。
- [[kv-prefix-radix]]：完整树实现，包含边中途命中与分裂。
- [[kv-prefix-radix-leases]]：pin/unpin 与叶子 LRU。
- [[p3a-xai-radix-cache]]：xAI 面经数据结构题，查询只认终结节点。
- [[sys-prefix-cache]]：通用命中条件与多用户风险。
- [[kv-prefix-block-hash]]：vLLM 式链式块哈希。
