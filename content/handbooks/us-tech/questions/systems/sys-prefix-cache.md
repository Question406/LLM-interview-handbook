---
id: sys-prefix-cache
section: systems
order: 7
level: A
title: 系统：prefix / prompt cache，多用户系统提示共享
quick: "Prefix cache 复用的是已经计算好的 KV 页，只有 token ID、模型权重、LoRA 与位置语义等条件一致才能命中。共享系统提示可以减少重复 prefill，但缓存占用同一块 HBM，要同时看命中收益、租户隔离和对在途请求的影响。"
tags:
  - vLLM
  - Serving
  - KV Cache
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: Automatic Prefix Caching — vLLM
    url: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
    type: secondary
  - title: SGLang — Fast Serving Framework with RadixAttention
    url: https://lmsys.org/blog/2024-01-17-sglang/
    type: secondary
  - title: PagedAttention — Hugging Face TGI
    url: https://huggingface.co/docs/text-generation-inference/main/conceptual/paged_attention
    type: secondary
---

Prefix cache 可以把同一段公共前缀的 KV 算一次、给多个请求复用，减少重复 prefill。关键是确认两次计算会得到相同 KV；字符串相同只是表面条件。

例如一条 2k token 的系统提示，hidden 和层数都大，千人共用时重复 prefill 是可观的 GEMM 开销。命中后只计算各自用户输入那一段，TTFT 就能缩短。vLLM automatic prefix caching、SGLang RadixAttention 和 TGI 的 KV 共享都在处理这个需求，底层寻址见 `sys-paged-attn`。

## 什么情况下能复用

Cache key 至少包含 token ID 序列、模型版本、LoRA / adapter、注意力配置，包括 sliding window 和位置编码。Tokenizer 或 chat template 不同，即使原文看起来一样，也应 miss。System prompt 改了一个空格，就要从第一个不同 token 处分叉；RoPE 起点与计算时的绝对位置也必须对上，不能把同一段 KV 随意接到不同位置。LoRA 改变有效权重，通常也不能复用 base 模型的前缀。错命中会让输出悄悄出错，比 miss 更难排查。

索引常见两种：vLLM 用块哈希，查公共前缀后从分叉块开始 prefill；SGLang 用基数树，把共享的 token 路径指向物理页，更自然地表达多轮或工具模板的部分共享。Agent 中稳定的公共段往往只有模板头，工具 schema 一改就分叉，要把稳定与易变部分分开缓存。

PagedAttention 可让多条 block table 指向同一物理块，用引用计数共享，各请求再独立增长。分页便于管理，但连续只读 prefix 也可保留，再和私有 suffix 分段读取，见 [[kv-prefix-segmented-attention]]。完整练习从 [[kv-prefix-implementation-index]] 开始，其中 [[kv-prefix-block-hash]] 检查上下文及祖先 key，[[kv-prefix-engine]] 把前缀 KV 真正交给 Transformer，验证减少重算。

## 共享后还要看什么

多租户要把 tenant / 安全边界加入 key。公共系统提示可以共享，用户文档默认不跨租户命中，隔离越严格，命中机会就越少。Key 漏掉 LoRA 或 template 版本会造成错命中，不能只检查 token。

页与 decode 共用 HBM，一条超长热门前缀可能挤掉在途请求的 KV。于是 hit rate 很高，P99 TPOT 却变差。淘汰采用 LRU / size-aware，并限制单前缀占比。跨机 replica 没有相同页面时，需要请求 affinity，或者接受 miss 重算。PD 分离时，prefill 池命中后 decode 池仍要取得 KV，见 `sys-prefill-decode-disagg`。

验收时我会同时报 hit rate、少算的 prefill token 数，以及缓存挤占的在途 KV 容量，才能判断实际收益。

## 追问

**只改一个字还能命中吗？**
只能复用第一个不同 token 之前的部分，整段仍命中说明 key 有误。

**磁盘 prompt cache 也这样设计吗？**
Key 的语义应一致，区别是 HBM 与存储介质。磁盘多一次访问延迟，更适合超长、重复率极高的文档前缀。

**命中率高但尾延迟更差，先查什么？**
先查热门前缀是否占满 KV 池、挤走正在 decode 的页，限制单 key 占用。

**LoRA 切换后能复用 base 前缀吗？**
通常不能。Adapter 改变有效权重，K/V 也变，必须区分 key。

**多租户一定拆 cache 吗？**
安全边界必须进入 key。可共享公共 system prompt，但用户文档默认不跨租户命中。

## 相关题

- [[xai-prompt-cache]]：租户隔离、RAG 前缀和 compaction 的取舍。
- [[sys-radix-tree]]：适合多轮和部分共享的 radix tree。
- [[kv-prefix-block-hash]]：链式块哈希如何编码上下文。
- [[sys-paged-attn]]：物理块的 refcount 和 CoW。
- [[meta-vllm]]：前缀缓存与分页、chunked prefill 的组合。
- [[kv-prefix-implementation-index]]：8 道实现题的入口。
