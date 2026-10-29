---
id: baichuan-case-library-construction
section: data
order: 101
level: A
title: 百川智能：Agent 的例子库应怎样创建？
quick: >-
  例子库是有 schema、有覆盖目标的检索集，我会按任务、难度、工具路径和失败模式 stratified sampling，脱敏去重，每条记下输入、正确
  action、证据和版本。检索时兼顾相似度和覆盖，再用 counterfactual / holdout 防模板泄漏和 overfitting。
tags:
  - Baichuan
  - Agent Data
  - Few-shot
  - Case Library
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 百川智能大模型实习一面 压力好大（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530'
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习；具体团队原帖未披露
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B（公司、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“例子库的创建流程”**

Agent 的例子库我会当成一个有字段和类型规范（schema）、有覆盖目标的检索集来建，按分组 sampling、过 data quality checks 再入库。把历史对话全量塞进 few-shot 不行，那只是日志镜像。

先定义它服务谁：给模型做 few-shot、给 Agent 选工具路线，还是给人工复盘，三种用途要的代表性和时效都不一样。候选来源有专家轨迹、线上成功 case、经验证器（verifier）过滤的合成样本，以及有代表性的 bad case。每条都脱敏、去重、统一 schema，并带上 taxonomy、输入条件、证据、预期 action / outcome、工具与环境版本、质量分、失效时间。

## 按覆盖 sampling

按意图、难度、语言、工具组合、失败类型分组。每组里选聚类代表样本，再加少量 edge cases，**禁止只挑最高分相似题**。检索目标是 $\mathrm{sim}(q,c)$ 和 diversity 的折中，同时受 token 预算约束。

实验我会这样设计。先固定检索条数 $k$，比较「纯相似度」和「相似度 + MMR / 分桶配额」两种检索。然后在 holdout 任务上测成功率、工具选对率，以及有没有抄到答案字符串。最后做 counterfactual：改掉一个关键约束，看这条例子是否仍被 retriever 当成近邻。比如例子是「把报表发给财务」，问题改成「把报表发给法务」，模型照抄例子里的收件人还判成「成功」，就说明它在抄答案。有答案泄漏时，改了约束命中应该变差，不该更好。

线上把用户纠正、工具失败、过期示例整理成候选，但必须过 data quality checks（verifier + 抽检）才写入。版本和环境 hash 对不上的例子降权或删掉。

## 追问

**为什么不能把历史对话全量堆进去？**
重复模板会占满 $k$ 条窗口，长尾失败模式永远进不了 context。

**怎么证明例子在帮忙，没在漏题？**
holdout 加 counterfactual：改了数字或约束还能成功，才算迁移；原文级的重叠要当污染处理。

**谁有权写入例子库？**
自动收集的数据只进入 candidate pool；正式写入要过 data quality checks、带失效时间，免得错误结论被固化下来。
