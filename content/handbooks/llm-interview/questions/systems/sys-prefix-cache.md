---
id: sys-prefix-cache
section: systems
order: 15
level: A
title: Prefix Cache 的命中条件和风险？
quick: >-
  只有 tokenized prefix、模型权重/adapter、position/attention semantics 等一致时才能安全复用
  KV；字符串看起来相同但 tokenizer/template/LoRA 不同可能不能命中。
tags:
  - Serving
  - Cache
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: vLLM PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

陷阱是「字符串看起来一样就能复用 KV」。Prefix cache 复用的是**已经算好的 K/V 页**，命中条件是 token 序列和计算语义一致，不是 UTF-8 一致。system prompt 改一个空格、chat template 不同、LoRA 不同，都应当 miss。错命中比 miss 更危险：静默用错前缀，输出错、还难查。实现上这些页通常挂在 PagedAttention 的 block table 上，见 `sys-pagedattention`。

## 命中要对齐什么

Cache key 至少包含：token IDs（不是原文）、model / 版本、adapter（LoRA）、相关 attention 配置（sliding window、sink、位置编码）。权重一变，旧 KV 全部作废。position 从 0 起算的绝对位置若和当时计算不一致，也不能复用。

字符串相同但 tokenizer 或 template 不同 → token 不同 → miss。Agent 的 dynamic system prompt、tool schema 一变，公共前缀就断。这就是「看起来能 cache、线上几乎不命中」。

## Agent 与多租户

带工具的多轮：真正稳的公共前缀往往只有模板头，后面每轮 schema / 检索片段都变。要提高命中，把稳定段和易变段切开，稳定段才进 cache。slime 多轮还必须 session affinity，否则页在 A 机、请求打到 B 机，等于强制 miss，见 `slime-router-session`。

多租户要按 tenant / 安全边界隔离，防止 cache poisoning：用户 A 的前缀页被用户 B 命中。隔离和命中率是反着的，不能只报 hit rate。

## 风险与淘汰

风险：错命中、租户串页、热点 prefix 占满显存、eviction 抖动。淘汰用 LRU / LFU / size-aware，并限制单前缀占比。验收看 hit rate、因 miss 多出来的 prefill token、以及有没有跨租户命中。Cache 不是免费的：页占着 KV 池，会挤掉在飞请求的 decode 容量。命中率高但 P99 TPOT 变差，往往是热点系统提示词把在飞 decode 的页赶走了。

## 追问

- **改了 system prompt 一个字？** 应从第一个不同 token 断开，整段旧 KV 不能用。若仍命中，key 设计错了。
- **LoRA 切换能复用 base 的 prefix 吗？** 一般不能。adapter 改了有效权重，K/V 不同。
- **和 prompt cache 磁盘方案？** 磁盘 / 跨请求持久化是另一层，仍要用同一套 key；只是介质从 HBM 换成存储。
- **命中率很高但 TPOT 变差？** 热点前缀占满 KV，在飞 decode 被挤。要 size-aware 淘汰，不能只追 hit。
- **chunked prefill 和 prefix cache 冲突吗？** 不冲突。切块算完的稳定前缀仍可落页；冲突来自模板/权变了，不是来自切块。
