---
id: baichuan-case-library-construction
section: data
order: 101
level: A
title: 百川智能：Agent 的例子库应怎样创建？
quick: >-
  例子库不是把历史对话全量堆进 few-shot；先按任务、难度、工具路径和失败模式分层采样，脱敏清洗并为每条示例
  记录输入、正确 action、证据和版本。检索时兼顾相似度与覆盖，且用 counterfactual / holdout 防止模板泄漏和过拟合。
tags:
  - Baichuan
  - Agent Data
  - Few-shot
  - Case Library
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 百川智能大模型实习一面 压力好大（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习；具体团队原帖未披露
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B（公司、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“例子库的创建流程”**

陷阱是把历史对话全量塞进 few-shot。例子库是有 schema、有覆盖目标的检索集，不是日志镜像。先定义服务对象：给模型 few-shot、给 Agent 选工具路线，还是给人工复盘——三者的代表性和时效不同。候选来自专家轨迹、线上成功 case、经 verifier 过滤的合成样本、以及代表性 bad case。每条脱敏、去重、统一 schema，并带 taxonomy、输入条件、证据、预期 action / outcome、工具与环境版本、质量分、失效时间。

## 覆盖采样，而不是最高分模板

按意图、难度、语言、工具组合、失败类型分桶。桶内取 cluster 代表 + 少量边界，**禁止只挑最高分相似题**。检索目标是 $\mathrm{sim}(q,c)$ 与 diversity 的折中，并受 token 预算约束。实验设计：

1. 固定检索条数 $k$，对比「纯相似度」vs「相似度 + MMR / 分桶配额」；
2. Holdout 任务上测成功率、工具选对率、是否抄到答案字符串；
3. Counterfactual：改一个关键约束，看例子是否仍被 retriever 当成近邻——若答案泄漏，命中应变差而不是更好。

线上把用户纠正、工具失败、过期示例回流为候选，但必须过质量门（verifier + 抽检）才写入。版本和环境 hash 不一致的例子降权或删除。

## 追问

- **为什么不能全量堆？** 重复模板占满 $k$ 条窗口，长尾失败模式永远进不了 context。
- **如何证明例子在帮而不是漏题？** Holdout + counterfactual：改数字/约束后仍成功，才是迁移；原文级重叠要当污染。
- **谁有权写入库？** 自动回流只进候选；写入要质量门与失效时间，避免错误结论固化。
