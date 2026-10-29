---
id: us-debug-vs-leetcode
section: overview
order: 4
level: A
title: 为什么美国 lab 爱给带 bug 的 Transformer，而不是再出一道中等 LeetCode？
quick: "Transformer debug 能检查你在真实代码中定位张量错误的能力：因果 mask、softmax 维度、缩放、位置编码以及 train / eval 切换都会一起出现。LeetCode 的算法题仍要准备，但无法替代这类训练代码练习。"
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

Transformer debug 能直接考察你是否理解训练代码里的张量形状、mask 和 cache 不变量。公开 OpenAI 电面记录里，有约 300 行代码、四个标注区间各藏一个 bug，修完还要加 KV cache；这能同时看出定位问题和扩展功能的能力。具体题见 `openai-transformer-debug`。

## 这轮测的能力

1. **先固定观测。** `eval()`、greedy、关 dropout。不固定的话你改对了也看不出来。
2. **按契约查，不按感觉改。** mask 必须在 softmax 前打 $-\infty$；softmax 沿 key 长；缩放是 $\sqrt{d_k}$；逐 token 生成（decode） 位置是 `cache_len`。
3. **加功能时不破坏旧不变量。** 有 cache 和没 cache，同一前缀 greedy 必须逐 token 相同。

这些检查针对真实模型代码。可以同时练 LeetCode，但准备 lab RE 岗时，要给张量调试留足时间。

## 和 Anthropic OA 的差别

Anthropic 更像「分层工程实现」：CRUD 对了才解锁 TTL，再解锁备份和并发。它更关注接口设计和状态机，Transformer debug 更关注张量计算。两类题都应先定位和完成要求，避免重构无关代码。见 `anthropic-inmemory-db`。

## 追问

**LeetCode 还要刷吗？**
Meta / Amazon / Microsoft 通用软件轮仍要。lab 的 RE 岗可以少刷 hard，但不能零。
**没给标注区间怎么办？**
自己加 shape 断言和「单 token vs 全量 attention」对齐测试，这就是工作方式。

## 相关题

- [[p3a-openai-transformer-bug-hunt]]：这里讲为什么考 debug，那张是可以直接练的版本，带一份植入了 mask 和位置 bug 的 attention 函数和测试。
