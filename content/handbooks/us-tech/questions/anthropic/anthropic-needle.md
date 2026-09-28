---
id: anthropic-needle
section: anthropic
order: 23
level: A
title: Anthropic：大海捞针不够，长上下文真实评测怎么设计？
quick: >-
  NIAH 只测能不能把一句正交事实抄出来，而且对 prompt 极敏感：Claude 2.1 加一句引导可以从约 27% 到约
  98%。真实评测要扫位置、用同分布干扰、测聚合 / 多跳 / 缺针拒答，并报告中间位置，不要只报平均准确率。
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

`anthropic-long-context` 已经讲过位置偏差和为什么 NIAH 是松上界。这张卡讲评测设计：Anthropic 自己复现过 Kamradt 的大海捞针，并写明一句 prompt 能把分数从大约 27% 拉到 98%。面试若只报「200k NIAH 满分」，会被当成没做过评测。材料来自官方长上下文博客和 Lost in the Middle / RULER。

## 为什么针不够，连针本身都不可信

标准针：干草堆是无关散文，针是「密码是 X」，问密码。检索和复制就够。它能抓「窗口根本读不到」，抓不住：

- 干扰项和问题同分布（多文档 QA）；
- 要聚合、计数、对账；
- 针有多根或要多跳；
- 针不存在时该拒答。

更糟的是度量本身不稳定。Claude 2.1 博客：模型常因为那句针看起来「不像在文档里」而拒绝回答；补一句「先给出上下文里最相关的句子」之后，整窗回忆几乎满。所以 NIAH 分数大量是拒答政策 + 提示词，不是「会不会用 200k」。评测协议必须冻结提示，并同时报「找到针」和「拒绝但其实找得到」。

Lost in the Middle 用多文档 QA：相关文档放中间，准确率掉成 U 形。RULER 把合成任务做成尺子：多针、可变追踪、聚合，很多宣称长窗的模型在这些任务上远小于广告长度。

## 一套我会提交的协议

1. 冒烟 NIAH。扫相对位置 $p \in \{0, 0.25, 0.5, 0.75, 1\}$ 和长度 $L$。只用来抓硬故障。提示固定，禁止「最相关句子」这类泄漏。
2. 缺针。干草堆里没有答案。正确行为是「资料里没有」，见 `anthropic-eval-honesty`、`anthropic-citations`。满分抄针但缺针乱编，是失败。
3. 同分布干扰。一篇相关、若干篇同主题干扰，只打乱顺序。这才接近 RAG。
4. 使用性。多跳（A 段的 ID 到 B 段的值）、计数、时间线、矛盾检测。Agent 场景把 tool 结果堆在中间，指令在两头——比保罗·格雷厄姆文集更像产品，见 Building effective agents。
5. 报曲线，不报一个平均。中间 20% 全灭会被平均藏住。同时扫 $L$，短窗还行、拉长就塌要分开写。

成本：全网格打 200k 会把预算烧在重复阅读上。先在 8k/32k 定协议并冻结提示和评分脚本，最大窗抽几个 $p$。离线用 `anthropic-batch-api`。标签切 documents 减少串角色，见 `anthropic-xml-prompt`，但不消灭 U 形。

## 错法和产品补丁

错法：针和干草堆主题完全无关却宣称「真实长上下文」；评测 prompt 在末尾重复答案；只测英文小说；用 NIAH 做训练目标（模型学会抄针，评测作废）。训练数据里也不要混进自己的 NIAH 针，否则热力图变绿、产品日志里的中间段照样丢。

产品补丁往往比等预训练消除 U 形更快：检索后重排，相关段放两端；先抽后读；中间位置做数据增强。声称 200k 产品能力，就要有 200k 的使用性套件，而不是一张绿热力图。

## 追问

- **NIAH 满分了还要测什么？** 缺针拒答、同分布 QA、聚合、多跳。NIAH 是检索上界。
- **那句引导算作弊吗？** 当产品提示可以；当「窗口能力」声明不行。能力数字必须标明提示。
- **和位置偏差是不是同一题？** 位置是机制假设；这里是评测设计。曲线怎么画见 `anthropic-long-context`。
- **RULER 能替代一切吗？** 不能。它仍是合成的。还要加你们真正的日志、工具轨迹、多文档客服集。
