---
id: pdd-long-context-cheap
section: systems
order: 120
level: A
title: 拼多多：Long Context 如何做到能看长文本但不太贵？
quick: "我会先检索、摘要或分块，让模型只读任务需要的内容；必须保留的长输入，再用前缀缓存、GQA 和 KV 量化降低成本。任务级预算要限制 prefill 和费用，评测则检查长依赖任务是否答对、引用是否忠实。"
tags:
  - PDD
  - Long Context
  - KV Cache
  - Cost
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 大模型算法二面-日常实习-拼多多
    url: https://www.nowcoder.com/feed/main/detail/a94c16e304bb40a188eeda38c5e973c8
    type: candidate-first-hand
  - title: GQA
    url: https://arxiv.org/abs/2305.13245
    type: primary
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：日常实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-03-15
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“Long Context 常见思路有哪些？在业务里如何做「能看长文本但不太贵」的折中?”**

要让长文本处理便宜，我会先减少必须送进模型的内容，再优化每个 token 的成本。检索、摘要和分块路由负责缩短输入，前缀缓存、GQA / KV 量化负责降低重复计算、显存和带宽开销。

比如长工单需要保留关键规则和相关证据，多商品对比需要读对 SKU 与字段，全文塞进 128K 窗口未必更有效。prefill 的 FLOPs 和 KV 显存都会随实际输入增长，所以要设任务级预算，并评估任务成功、引用忠实和单次成本。针-in-haystack 只能覆盖其中一部分能力。

## 先缩短再进模型

常见技术栈：更长预训练、位置外推 / 插值（NTK、YaRN）、稀疏或分块 attention、prefix cache，以及检索把「需要读的部分」变短。业务优先级：

1. 先检索再读：商品页、政策、工单用 检索增强生成（RAG） / 结构化字段，只把相关片段送进模型。ANN + 倒排，见向量卡。
2. 分层摘要：超长会话先压成记忆要点，必要时再回看原文句柄，不要每轮重放全文。
3. 分块路由：并行读多块再 copilot 聚合，避免单次 $O(n^2)$ 全量 attention。块间丢失交叉证据时，再对冲突块做第二轮精读。

静默截断关键条款是事故；超过预算应走摘要或拒答「请缩小范围」。

## 系统侧压每 token 成本

GQA / MQA 让 KV head 少于 Q head，cache 体积近似按 $n_{\mathrm{kv}}/n_q$ 降。KV 量化（INT8/FP8）再降一档带宽，要盯质量。Prefix cache 复用系统提示和固定政策模板；key 带文档版本，政策一改不能复用旧 KV。Continuous batching + PagedAttention 让不同长度共存，避免按最大窗口 padding。限制 `max_prefill_tokens`：超了切块或拒。投机解码对长 prefill 帮助有限，别当长上下文银弹。训练侧长序列几乎必开 activation checkpoint；那是训练显存，和推理 KV 是两本账。

Serving 预算按任务：客服工单给 8k 有效 token，整店目录不允许。成本按 billed token × 单价，塞满窗口就是烧钱。



针-in-haystack 只证明位置外推还在。业务要：多 SKU 对比是否引用对 id、长规则是否漏关键除外条款、单次费用是否在预算内。中间遗忘见下一张卡。实际处理时，可以先检索缩短输入，再用摘要保留状态，让窗口主要容纳近轮原文和命中的证据。

## 追问

**128K 模型是不是就不贵了？**
不是。prefill FLOPs 和 KV 仍随实际填入的 $N$ 涨。宣称长度是能力上限，账单和延迟按真正塞进窗口的 token 算。默默填满就是烧钱。
**GQA 省什么？**
省 KV 体积和 逐 token 生成（decode） 带宽，系数是 $n_{\mathrm{kv}}/n_q$。不省 Q 侧计算，也不代替检索。和 FlashAttention 正交：一个减 cache 体积，一个减注意力 I/O 形状。
**为什么针-in-haystack 不够？**
它只证明某个位置还找得着。业务要的是多 SKU 对比是否引用对 id、长规则是否漏除外条款、单次费用是否在预算内。找得着不等于看得对。
**静默截断为什么不行？**
合同和促销规则被砍掉除外条款会错卖。超过 `max_prefill_tokens` 应摘要、分块或拒答「请缩小范围」，并让用户知道看不全。
**和更大窗口那题怎么分？**
本题是怎么便宜地看长；那题是为什么更大不一定更好。先检索再谈窗口。两张卡加上溢出策略才是一套方案。
