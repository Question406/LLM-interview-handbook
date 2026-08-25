---
id: us-debug-vs-leetcode
section: overview
order: 4
level: A
title: 为什么美国 lab 爱给带 bug 的 Transformer，而不是再出一道中等 LeetCode？
quick: >-
  他们要的信号是：你能不能在真实训练代码里定位张量契约错误，而不是会不会双指针。Debug 轮把因果
  mask、softmax 维、缩放、位置编码、train/eval 混用一次性摊开；LeetCode 测不了这些。
tags:
  - Debug
  - OpenAI
  - 备考
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: OpenAI Research Engineer Interview Guide (Exponent)
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: OpenAI MLE phone screen Transformer debugging (1Point3Acres)
    url: https://www.1point3acres.com/interview/thread/1134115
    type: candidate-first-hand
---

OpenAI 电面给一份约 300 行的 Transformer、四个标注区间各藏一个 bug，改完再加 KV cache，几乎是公开面经里最能说明「美国 lab 在考什么」的一张快照。见 `openai-transformer-debug`。

## 这轮测的能力

1. **先固定观测。** `eval()`、greedy、关 dropout。不固定的话你改对了也看不出来。
2. **按契约查，不按感觉改。** mask 必须在 softmax 前打 $-\infty$；softmax 沿 key 长；缩放是 $\sqrt{d_k}$；decode 位置是 `cache_len`。
3. **加功能时不破坏旧不变量。** 有 cache 和没 cache，同一前缀 greedy 必须逐 token 相同。

这些和「最长回文子串」不是同一块肌肉。可以并行刷题，但权重别倒过来。

## 和 Anthropic OA 的差别

Anthropic 更像「分层工程实现」：CRUD 对了才解锁 TTL，再解锁备份和并发。测的是接口设计和状态机，不是张量。两家都讨厌你一上来重构无关代码。见 `anthropic-inmemory-db`。

## 追问

- **LeetCode 还要刷吗？** Meta / Amazon / Microsoft 通用软件轮仍要。lab 的 RE 岗可以少刷 hard，但不能零。
- **没给标注区间怎么办？** 自己加 shape 断言和「单 token vs 全量 attention」对齐测试，这就是工作方式。
