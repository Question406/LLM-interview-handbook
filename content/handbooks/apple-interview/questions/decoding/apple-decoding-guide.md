---
id: apple-decoding-guide
section: decoding
order: 0
level: S
title: Decoding 练习路线：greedy、beam search、sampling 与约束 decoding 怎么选？
quick: >-
  先写 [B,V] 的批量 token selection，再接入带独立 EOS、left padding 和 KV cache 的
  greedy/sampling 生成循环，最后做完整 batched beam search。原单序列、单步与进阶题仍保留，并明确各自支持范围。
companies:
  - apple
tags:
  - Apple
  - Decoding
  - Beam Search
  - 备考路线
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Apple AIML 研究团队候选人原帖，仅支持手写 beam search 题型
    url: 'https://www.1point3acres.com/bbs/thread-1145563-1-1.html'
    type: interview
  - title: Google's Neural Machine Translation System
    url: 'https://arxiv.org/abs/1609.08144'
    type: primary
---

本章整理 decoding 算法与代码练习，不把迁移题改称 Apple 原题。先前经 Chrome 核对的 2025-09-13 Apple AIML 研究团队原帖明确提到手写 beam search；原帖没有公开完整接口、分数规则或 EOS 细节，也未确认本次 AFM Data Team。下面练习沿用各原题卡明确的手册约定，本卡只是学习路线。

## 从哪里开始写 batch inference

新增三张独立编程卡，都包含完整题面、可复制代码、真实 attention 测试 adapter 与可运行 assertions。先做 [[apple-batched-token-selection]]，再做 [[apple-batched-generation]]，最后做 [[apple-batched-beam-search]]。

| 实现 | 单步 batch 选择 | 完整 batch 生成 | 说明 |
| --- | --- | --- | --- |
| `apple-batched-token-selection` | 是，[B,V] → [B] | 否 | Greedy、temperature/top-k/top-p、multinomial、Gumbel；每行参数独立 |
| `apple-batched-generation` | 是 | 是 | 不同 prompt 长度、left padding、独立 EOS、positions、真实 KV；三种选择方法共用循环 |
| `apple-batched-beam-search` | 是，[B,K,V] | 是 | 完整循环、parent backpointer、重复 parent、finished carry、cache gather、最终 length penalty |
| `coding-topk-nucleus` / `apple-topk-sample` | 否，[V] | 否 | 原单请求单 token 入门题 |
| `coding-beam-search` | 否，单 prompt | 否 | 单请求完整 beam；width=1 是单请求 greedy |
| `code-beam-search` | 是 | 否 | 只做一次 beam 扩展 |
| `coding-gumbel-max` | 是 | 否 | 向量化单步选择；完整循环见新 generation 卡 |
| `coding-spec-accept` | 不要求 batch | 否 | 仍是单条 speculative verification block，不是完整 draft/target batch serving |
| `msft-constrained-decode` | 概念讨论 | 否 | 新卡用 allowed_fn 接收逐行合法集合，但不含 JSON grammar compiler |

这里的完整生成是 **static batching**：请求一起开始，结束后保留 slot。Active compaction、continuous batching、生产框架 Cache adapter 和 GPU 性能优化仍是另外的工程扩展。测试在 CPU/PyTorch 跑通，没有测 GPU latency 或 throughput。

## 原单序列与进阶练习顺序

| 顺序 | 题目 | 需要独立完成什么 |
| --- | --- | --- |
| 1 | `coding-beam-search` | 先把宽度设为 1 写 greedy，再实现多条候选的完整循环；处理 EOS、步数上限、累计 logprob 和最终 length penalty |
| 2 | `code-beam-search` | 从 `[B,K,V]` 候选分数做全局 top-k，整除和取模还原父 beam 与新 token；说明如何重排前缀与 KV cache |
| 3 | `apple-topk-sample`、`coding-topk-nucleus` | 温度、非法 token mask、top-k、累计概率 top-p 和重新 normalization；保留跨越概率阈值的 token |
| 4 | `coding-gumbel-max` | 使用独立噪声做类别 sampling，区分硬 sampling 温度与 Gumbel-softmax 松弛温度 |
| 5 | `coding-spec-accept` | 按位置验证草稿，第一次拒绝后做残差 resampling；全接受时增加 bonus token，说明 KV 回滚由谁处理 |
| 6 | `msft-constrained-decode` | 按当前文法状态构造下一 token 的合法集合，并分别评价格式正确性与任务正确性 |

这些题中有 Apple 标签练习，也有公开算法和其他公司的迁移材料；标题、公司和来源保持原样。on-device speculative decoding 的硬件取舍另见 `apple-spec-edge`。

## 最容易混淆的接口

完整 beam search 包含循环、已结束候选和终止规则；beam step 只是一次选择，不能把它说成完成整个生成器。top-k 要在所有 beam 的候选间比较，不能每条 beam 各做一次 argmax 就算完成 beam search。

搜索阶段按原始累计分数筛候选，与最终使用 length penalty 重排是不同算法。本章完整实现明确采用最终重排，不承诺全局最优，也不能直接当成所有框架的 beam search 行为。

## 面试时怎样验证

先用只有两个词的确定分布手算一到两步，再测试立即 EOS、全部结束、步数为零、同一父 beam 被选出多个子候选及分数 tie。随机 sampling 测试固定 seed，分布检查使用足够样本和合理容差；不能以一次 sampling 结果证明概率正确。

如果面试官给的是论文或半成品代码，先明确输入是 logits、概率还是 log probability，再确认特殊 token、禁用 token、长度与终止语义。算法正确与质量更好仍是两件事，最终要在相同 inference budget 下比较任务结果、延迟与多样性。
