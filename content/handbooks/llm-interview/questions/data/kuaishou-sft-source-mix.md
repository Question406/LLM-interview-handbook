---
id: kuaishou-sft-source-mix
section: data
order: 123
level: A
title: 快手：SFT 阶段不同来源数据如何配比？
quick: >-
  先按目标能力分组（通用指令、垂域问答、chain of thought（CoT，即分步推理过程）），每组建
  holdout，看加进去的边际收益和对其他组的遗忘，别拍死 1:1:1。配比按覆盖缺口、质量分和长度 / 难度调，safety 与 format
  regression examples 单独留配额，依据就是那张 ablation 表。
tags:
  - Kuaishou
  - SFT Data
  - Data Mixture
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 快手26校招大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/b1da5731c34e4a3d99becef4f0a0c169'
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 校招；一面
- 面试时间：原帖未披露；帖子发布于 2025-12-30
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“在 SFT 阶段，你们如何设计不同来源数据（如通用指令、垂域问答、CoT 数据）的配比？依据是什么？”**

我会先说清 SFT 要保住哪些能力，通用指令、垂域事实、推理格式、安全拒答，每一类建独立的 holdout，然后按覆盖缺口和有效 token 调配比。依据就是一张能复述的表：加了哪类数据，这类升了多少，别的类掉了多少，再配上遗忘曲线和业务 slice。一面上来就说「经验上 1:1:1」或者「CoT 多一点更好」，面试官一定会追问依据，没有这张表就答不上来。

举个例子，短 FAQ 一万条，可能还抵不过两百条可验证的 CoT。所以哪一类 holdout 最差、线上错误桶最大，就提高这一类的有效 token，原始条数说明不了什么。快手是内容加搜索的场景，还要防着垂域事实源把通用闲聊和安全锚挤掉。遗忘往往比「垂域分又高了一点」更早暴露成线上事故。

## 根据覆盖缺口和有效 token 调配比

除了看缺口，还要看质量和难度。高置信的人工样本和过了强验证器（verifier）的样本权重给大一些；过长的 CoT 和模板改写降权，免得占满梯度。data quality checks 的做法见 `meituan-label-quality`。

几类数据各有分工。通用指令当锚，防止垂域 SFT 以后不会聊天了；CoT 只给真正需要中间计算的切片，否则所有短问答都会被拉长；安全和格式样本单独留配额，不跟业务数据抢。比起一次拍死比例，用 temperature mixing 或 curriculum 更稳：先训格式和通用，再提高垂域和难例的温度。这和美团的难易配比（`meituan-easy-hard-sft-balance`）是同一套分组统计的思路，只是轴从难度换成了来源。

快手业务上还要把「看起来像垂域」和「真能答对站内事实」分开。垂域问答如果没有可核对的字段或检索依据，加多了可能只是让模型学会了领域措辞。CoT 源也要先过 executable checks（计算、代码、规则），再进配比；未通过 checks 的长推理按低质源降权，不能因为「有 chain of thought」就抬温度。

## 用对照实验说明依据

对照至少四组：等比例、按缺口加权、按质量加权、curriculum。每组都报各个 holdout、遗忘（通用和安全有没有掉），以及平均完成长度。如果条数涨了但某个桶的 holdout 掉了，说明配比是在稀释，没有补到模型容易失败的任务上。SFT 管线（`data-sft-pipeline`）里的 source-level ablation 就是这张表，看的是 $\Delta$ 能力 / $\Delta$ token，「这个源看起来更像业务」不算依据。overfitting 防护（`meituan-sft-overfit`）要一起做，否则调高某个源只是在背那一批模板。比例是实验的结果，一开始只是假设。

## 追问

**为什么不用固定的 1:1:1？**
条数不等于有效梯度。短模板会淹没难例，要按 holdout 缺口和 token 效率来调。

**CoT 是不是越多越好？**
不是。只给需要中间计算的切片；全量拉长会伤到短问答的延迟和格式。

**垂域数据加太多会怎样？**
通用指令和安全锚会先掉。先看遗忘曲线，再决定要不要提高垂域的温度。

**面试官追问依据，还要拿出什么？**
一张 ablation：「加这一类 token → 这一类升多少、相邻的类掉多少」。只报经验比例不够。
