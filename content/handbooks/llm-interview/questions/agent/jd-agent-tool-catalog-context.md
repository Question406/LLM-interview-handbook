---
id: jd-agent-tool-catalog-context
section: agent
order: 110
level: S
title: 京东科技：工具上下文太长、工具列表太多时如何治理？
quick: >-
  将完整工具目录留在 registry，按任务做分层路由和渐进披露；只向模型暴露候选工具的短 schema，必要时检索
  详细文档。以权限、版本和评测控制召回，工具调用失败后回退扩展候选集，而非把所有定义塞入 context。
tags:
  - JD Technology
  - Agent
  - Tool Routing
  - Context Engineering
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 京东科技 AI 全栈 agent 研发一面面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e80b257b1c064970a72c9679c2177585?sourceSSR=post&weFlow=true
    type: candidate-first-hand
---

## 真题记录

- 公司：京东科技
- 团队 / 岗位：AI 全栈 Agent 研发
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露；帖子发布于 2026-06-11
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“如果一个工具调用上下文太长了，你怎么处理”；“当你的工具列表太多了，工具很多，你想怎么优化”**

陷阱是把完整工具目录一次性塞进 prompt。列表变长后，选错率、token、注入面一起涨。京东科技这面要把工具看成带权限、版本、成本和副作用的检索对象：完整目录留在 registry，模型只看到当前候选的短 schema。路由总览见 `agent-tool-routing`，渐进披露见 `agent-skill-progressive`，选错纠正见 `byte-react-tool-select`。

## 目录留在 registry，窗口里只放候选

先用任务 intent、实体、用户权限和业务域过滤，再用 embedding / 词法路由或轻量分类器召回少量候选。第一轮只给名称、单行能力、风险等级、必填字段；模型选中后再加载完整 schema、示例和 policy。权限过滤必须在检索前：没有 ACL 的工具不能因为 description 相似被召回，否则路由等于越权通道。

候选集大小用评测定：看工具选择准确率与 recall@k，而不是固定「永远 5 个」。置信不足或调用失败，先扩大候选或向用户澄清，再允许搜 registry；不要一失败就把全量目录倒进窗口。

## 单次调用 Observation 太长：抽字段、留句柄

工具返回整页 JSON、长 HTML、大表时，不要原样回灌。结构化抽取当前任务需要的字段，保留分页 token / 对象 ID 作为句柄，原始结果进可检索缓存。需要细节再按句柄二次读取。这和对话三级压缩是同一思想：近处留能行动的原文，远处留句柄，见 `byte-three-level-compress`。

截断要可逆：日志里能找回原文，模型窗口里只放摘要。不可逆截断会导致下一步填错 ID。对超长 observation 做 schema 级白名单字段，比让模型「自己总结一下」更稳。

## 版本、评测、失败回退

目录更新要版本化和 deprecation，防止旧 schema 或同名不同义接口还在被调用。评测 router：recall@k、工具选择准确率、token/latency、错误副作用、候选集变化后的回归。这些指标属于 Agent 评测，不只是 QA 准确率，见 `jd-agent-eval-beyond-qa`。

失败回退：schema 校验失败可提示缺哪一字段；选错工具则扩大候选而不是重复非法调用。严禁让检索到的 description 自动提升权限。成本高或副作用大的工具在短 schema 里就要标风险，执行层再卡一道，而不是等模型自觉。电商工具尤其多同名「查单 / 改单」：短描述必须写清读还是写、作用在哪张表。列表治理失败的典型症状是模型每次都调最通用的那一个搜索接口，再在超长 JSON 里自己找字段——这正是「上下文太长」和「工具太多」同时爆发的形态。

## 追问

- **路由错了漏召回怎么办？** 保留「搜索工具目录」的元工具，并在失败时扩大 k。同时用 recall@k 盯着，避免只优化 token。
- **和 Skill 渐进披露是一回事吗？** 同类：先目录后展开。Skill 是程序化知识包，工具是可执行 API；两者都可以检索，但权限模型不同。
- **同名工具怎么防调错？** 用完全限定名 + 版本，短描述写清业务域（订单 vs 售后），不要只靠模型读一句介绍。
- **上下文长是因为对话历史还是工具定义？** 先拆开测。工具定义用本卡的分层披露；对话历史用压缩，不要用同一种截断硬砍。
