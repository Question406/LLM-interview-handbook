---
id: anthropic-needle
section: anthropic
order: 23
level: A
title: Anthropic：大海捞针不够，长上下文真实评测怎么设计？
quick: "我会固定提示与评分协议，先用 NIAH 检查窗口，再加缺针拒答、同主题干扰、聚合和多跳任务，并扫描位置与长度。Claude 2.1 的公开测试中，一句引导就能把分数从约 27% 拉到约 98%，所以分数必须连同提示、拒答情况和中间位置表现一起报告。"
tags:
  - Anthropic
  - Long context
  - Evaluation
  - Needle
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Long context prompting for Claude 2.1
    url: https://www.anthropic.com/news/claude-2-1-prompting
    type: primary
  - title: Lost in the Middle — How Language Models Use Long Contexts
    url: https://arxiv.org/abs/2307.03172
    type: primary
  - title: RULER — What's the Real Context Size of Your Long-Context Language Models?
    url: https://arxiv.org/abs/2404.06654
    type: primary
---

我会冻结提示和评分协议，把 NIAH 当冒烟测试，再测缺针、同主题干扰和需要汇总多处信息的任务。例如「密码是 X」可以直接复制，A 段给 ID、B 段给对应值的多跳任务就需要真正使用上下文。位置偏差的机制和曲线见 `anthropic-long-context`，这里重点是如何把这些测试组成协议。

## 先排除提示和拒答政策的影响

标准针：干草堆是无关散文，针是「密码是 X」，问密码。检索和复制就够。它能抓「窗口根本读不到」，抓不住：

- 干扰项和问题同分布（多文档 QA）；
- 要聚合、计数、对账；
- 针有多根或要多跳；
- 针不存在时该拒答。

Anthropic 在 Claude 2.1 博客中复现 Kamradt 的测试时，发现模型常因针看起来「不像在文档里」而拒答。补上「先给出上下文里最相关的句子」，分数就从大约 27% 升到 98%，整窗回忆几乎满分。这说明分数受到拒答政策和提示词的很大影响。协议必须固定提示，同时记录找到针和本来找得到却拒答的情况。

Lost in the Middle 用多文档 QA：相关文档放中间，准确率掉成 U 形。RULER 把合成任务做成尺子：多针、可变追踪、聚合，很多宣称长窗的模型在这些任务上远小于广告长度。

## 按什么顺序测试

1. 冒烟 NIAH。扫相对位置 $p \in \{0, 0.25, 0.5, 0.75, 1\}$ 和长度 $L$。只用来抓硬故障。提示固定，禁止「最相关句子」这类泄漏。
2. 缺针。干草堆里没有答案。正确行为是「资料里没有」，见 `anthropic-eval-honesty`、`anthropic-citations`。满分抄针但缺针乱编，是失败。
3. 同分布干扰。一篇相关、若干篇同主题干扰，只打乱顺序。这才接近 检索增强生成（RAG）。
4. 使用性。多跳（A 段的 ID 到 B 段的值）、计数、时间线、矛盾检测。Agent 场景把 tool 结果堆在中间，指令在两头，比保罗·格雷厄姆文集更像产品，见 Building effective agents。
5. 报曲线，不报一个平均。中间 20% 位置的失败会被平均分掩盖。同时扫 $L$，短窗还行、拉长就塌要分开写。

成本上，全网格打 200k 会消耗大量重复阅读预算。先在 8k/32k 定协议并冻结提示和评分脚本，最大窗抽几个 $p$。离线用 `anthropic-batch-api`。标签切 documents 减少串角色，见 `anthropic-xml-prompt`，但不消灭 U 形。

常见误区是：针和干草堆主题完全无关却宣称「真实长上下文」；评测 prompt 在末尾重复答案；只测英文小说；用 NIAH 做训练目标（模型学会抄针，评测作废）。训练数据里也不要混进自己的 NIAH 针，否则热力图变绿、产品日志里的中间段照样丢。

产品侧可以先试检索后重排，把相关段放两端，或先抽取再读；训练时对中间位置做数据增强。这通常比等待预训练消除 U 形更快。200k 产品能力的声明，也要由相应长度的使用性测试支持。

## 追问

**NIAH 满分了还要测什么？**
缺针拒答、同分布 QA、聚合、多跳。NIAH 是检索上界。

**那句引导算作弊吗？**
当产品提示可以；当「窗口能力」声明不行。能力数字必须标明提示。

**和位置偏差是不是同一题？**
位置是机制假设；这里是评测设计。曲线怎么画见 `anthropic-long-context`。

**RULER 能替代一切吗？**
不能。它仍是合成的。还要加你们真正的日志、工具轨迹、多文档客服集。
