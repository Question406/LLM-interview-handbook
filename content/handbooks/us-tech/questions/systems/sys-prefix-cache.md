---
id: sys-prefix-cache
section: systems
order: 7
level: A
title: 系统：prefix / prompt cache，多用户系统提示共享
quick: >-
  复用的是已经算好的 KV 页，不是字符串。Token ID、权重、LoRA、位置语义都一致才能命中。多用户同一条
  system prompt，分页下用引用计数共享物理块；模板或权重一变，必须从分叉 token 断开。
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

## 题怎么来的

Chat 产品几乎都有一条很长的系统提示，成千上万用户共用。vLLM automatic prefix caching、SGLang RadixAttention、TGI 的 KV 共享，问的都是：这段 KV 能不能算一次、给多人用。NVIDIA 推理岗会追页表怎么共享；应用岗会追错命中和租户隔离。底层寻址见 `sys-paged-attn`，本题管命中条件和多租户。

## 命中的是 KV 页，不是 UTF-8

Prefix cache 复用的是已经算好的 K/V 块。Cache key 至少要包括：token ID 序列（不是原文）、模型版本、LoRA / adapter、注意力配置（sliding window、位置编码）。字符串看起来一样但 tokenizer 或 chat template 不同，token 就不同，应当 miss。System prompt 改一个空格，从第一个不同 token 断开，整段旧 KV 不能用。

位置要从当时计算的绝对位置对上。把一段 KV 接到另一条长度不同的请求后面、RoPE 起点错了，数值是错的。LoRA 一切，有效权重变了，base 模型的 prefix 也不能复用。错命中比 miss 更危险：输出 silently 错，还难查。

实现上有两条常见索引：

- **哈希前缀：** vLLM 对块内 token 做 hash，按块查找。公共前缀命中后，从分叉块开始 prefill。
- **基数树：** SGLang RadixAttention 把 token 前缀树的节点指到物理页，多条请求走同一条根到分叉。树比扁平哈希更适合大量部分共享（多轮、工具调用模板头相同、后面分叉）。

PagedAttention 的引用计数让共享便宜：多条 block table 指向同一物理块。没有分页，共享意味着 memcpy 一份连续 buffer，系统提示一长就划不来。

## 多用户系统提示：收益和风险

一条 2k token 的系统提示、hidden 大、层数多，prefill 本身是一笔可观的 GEMM。千人共享时，命中可以把 TTFT 从「整段 prefill」变成「只算用户那截」。这是产品里最值得开 prefix cache 的形状。Agent 多轮里真正稳的公共前缀往往只有模板头，工具 schema 一变就断；要把稳定段和易变段切开，只有稳定段进 cache。

风险：

- **错命中：** key 漏了 LoRA 或 template 版本。
- **租户串页：** 用户 A 的前缀被用户 B 命中。多租户要在 key 里加 tenant / 安全边界，命中率和隔离是反着的。
- **热点挤占：** 一条超长系统提示占满 KV 池，把在飞 decode 的页赶走，hit rate 很高但 P99 TPOT 变差。淘汰要用 LRU / size-aware，并限制单前缀占比。
- **跨机 miss：** 请求打到没有这份页的 replica。要 affinity，或接受 miss 重算。PD 分离时，prefix 命中在 prefill 池，decode 池仍要拿到对应 KV，见 `sys-prefill-decode-disagg`。

Cache 不是免费的：页占着和 decode 同一块 HBM。我会报 hit rate、因命中少算的 prefill token、以及对在飞 KV 容量的挤出，而不是只报「开了 prefix cache」。

## 追问

- **改了系统提示一个字？** 从第一个不同 token 断开。若仍命中，key 设计错了。
- **LoRA 切换能复用 base 的 prefix 吗？** 一般不能。Adapter 改了有效权重，K/V 不同。
- **和磁盘 prompt cache 是一层吗？** 介质不同（HBM vs 存储），key 语义应当同一套。磁盘方案多一跳延迟，适合超长、重复极高的文档前缀。
- **命中率很高但尾延迟变差？** 热点前缀挤掉在飞 decode。要限制单 key 占用，不要只追 hit。
- **多租户必须拆 cache 吗？** 安全边界必须进 key。共享 system prompt 可以跨用户；用户文档前缀默认不要跨租户命中。
