---
id: sys-prefix-cache
section: systems
order: 15
level: A
title: Prefix Cache 的命中条件和风险？
quick: 假设很多请求都有相同的 system prompt。如果这段内容的计算条件也相同，就可以复用已经算好的 prefix KV，减少重复 prefill。
tags:
  - Serving
  - Cache
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: vLLM PagedAttention
    url: 'https://arxiv.org/abs/2309.06180'
    type: primary
---

## 回答思路

> **问题与场景：** 假设很多请求都有相同的 system prompt。
>
> **做法与原因：** 复用前要确认的不只是原文字符串。
>
> **检查与取舍：** 我会同时看省下的 prefill 工作与缓存占用。

## 可以这样回答

假设很多请求都有相同的 system prompt。如果这段内容的计算条件也相同，就可以复用已经算好的 prefix KV，减少重复 prefill。

复用前要确认的不只是原文字符串。Token IDs、有效模型权重、adapter、位置和 mask 的语义都要一致。用户私有数据还要按授权范围隔离，不能为了提高 hit rate 跨用户共享。

我会同时看省下的 prefill 工作与缓存占用。缓存也使用显存，可能挤掉正在生成的请求；因此 hit rate 提高但整体 latency 变差，是完全可能发生的。

## 技术备查

Prefix cache 只有在 token 序列和计算语义一致时，才能复用已经算好的 K/V 页。比如 system prompt 改一个空格、chat template 不同或 LoRA 不同，都应当 miss；只比较 UTF-8 文本会漏掉这些条件。错命中会让模型悄悄使用错误的历史状态，输出出错也很难排查。实现上，这些页通常挂在 PagedAttention 的 block table 上，见 `sys-pagedattention`。

## 命中要对齐什么

Cache key 至少包含：token IDs（不是原文）、model / 版本、adapter（LoRA）、相关 attention 配置（sliding window、sink、位置编码）。权重一变，旧 KV 全部作废。position 从 0 起算的绝对位置若和当时计算不一致，也不能复用。

字符串相同但 tokenizer 或 template 不同 → token 不同 → miss。Agent 的 dynamic system prompt、tool schema 一变，公共前缀就断。这就是「看起来能 cache、线上几乎不命中」。

带工具的多轮：稳的公共前缀往往只有模板头，后面每轮 schema / 检索片段都变。要提高命中，把稳定段和易变段切开，稳定段才进 cache。slime 多轮还必须 session affinity，否则页在 A 机、请求打到 B 机，等于强制 miss，见 `slime-router-session`。

多租户要按 tenant / security constraints 隔离，防止 cache poisoning：用户 A 的前缀页被用户 B 命中。隔离和命中率是反着的，不能只报 hit rate。

## 风险与淘汰

除了错命中和租户串页，还要防止热点 prefix 占满显存、淘汰频繁抖动。可以用 LRU / LFU / size-aware 淘汰，并限制单个前缀占比。验收时看 hit rate、因 miss 多算的 prefill token，以及有没有跨租户命中。Cache 不是免费的：页占着 KV 池，会挤掉正在生成的请求可用的 KV 容量。命中率高但 P99 TPOT 变差，往往是热点系统 prompt 把正在生成的请求所用的 KV 页淘汰了。

## 追问

**改了 system prompt 一个字？**
应从第一个不同 token 断开，整段旧 KV 不能用。若仍命中，key 设计错了。
**LoRA 切换能复用 base 的 prefix 吗？**
一般不能。adapter 改了有效权重，K/V 不同。
**和 prompt cache 磁盘方案？**
磁盘 / 跨请求持久化是另一层，仍要用同一套 key；只是介质从 HBM 换成存储。
**命中率很高但 TPOT 变差？**
热点前缀占满 KV，正在生成的请求可用的 KV 空间被挤占。要 size-aware 淘汰，不能只追 hit。
**chunked prefill 和 prefix cache 冲突吗？**
不冲突。切块算完的稳定前缀仍可落页；冲突来自模板/权变了，不是来自切块。
