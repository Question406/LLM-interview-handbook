---
id: byte-token-cost-debug
section: systems
order: 200
level: A
title: 字节秋招一面：Agent Token 涨得太快，怎么定位和压？
quick: "按 turn 拆：system、工具 字段和类型规范（schema）、检索回写、历史。先砍重复工具回传和未压缩日志，再缩候选工具，最后才换小模型。定位依靠每步的 token 消耗记录，别先改温度。"
tags:
  - ByteDance
  - Token Cost
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节AI Agent开发秋招一面面经
    url: https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：AI Agent 开发；秋招一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如果发现Agent运行过程中Token消耗增长过快，会如何定位问题并进行优化？”**

常见误区是：先改温度或换小模型。Token 涨得快，先按 turn 做账本：system、工具 字段和类型规范（schema）、检索回写、历史、completion。常见元凶是整页 JSON、全量工具目录、压缩没开、循环重试。优化顺序是结构化抽取 → 渐进披露工具 → 三级压缩 → 缓存幂等读；「降本」和「丢约束」要分开验收。适用多轮、工具返回大、历史变长；单轮短问答更可能是定价或重试风暴。相关卡：`byte-three-level-compress`、`xiaohongshu-mcp-skill-token-efficiency`。定位没完成前不要同时开压缩和换模型。

## 先记录各类开销，再优化

每步记录各类 token 数，画堆叠图看哪一类占比最大。改一类、复测一类，不要同时改温度、模型和压缩。典型账：第 1 轮 8k，第 8 轮 80k，每轮把 `pytest -q` 二十页日志和四十个工具 schema 原样塞回。定位对了，优化才有对象。硬约束（路径、测试命令、禁止改的文件）压缩后还要对得上，否则省下来的 token 会变成更多轮重试，总成本反而升。账本要按 request id 落盘，事后才能证明是 schema 膨胀还是 观测结果（observation） 膨胀，而不是凭感觉砍 输入提示（prompt）。

## 压的顺序：回写、工具面、历史

先对日志 / 检索做失败栈或字段抽取，只留相关数十行。工具按当前阶段渐进披露，例如编码中只暴露 `read_file` / `run_test` / `apply_patch`。历史用近轮原文 + 中期摘要。幂等读结果缓存，避免同一 URL 每轮回灌。换小模型是最后一步，因为它同时改质量与价格，会把实验搅浑。三级压缩（近轮原文、中期摘要、远期丢弃）要写成策略而不是每次让模型自己决定留什么。

## 失败模式与回归

只砍长度不看任务成功率：关键 Observation 被砍掉后模型更爱重试，token 反而升。用「压缩前后硬约束清单」回归，确认失败用例名、路径和断言还在。线上按成分告警：schema 占比、observation 占比、重试轮次。循环重试要设轮次预算和同类错误熔断，否则压缩省下的 token 会被死循环吃回去。顺序是：账本 → 砍回写 → 缩工具面 → 摘要历史 → 最后才动模型。

## 追问

- **怎么证明定位对了？** 堆叠图上改动的那一类明显下降，且任务成功率不掉。一次只改一类 token，才能把因果说清楚。
- **system prompt 能不能一起砍？** 可以版本化精简，但安全与 schema 约束优先于文学性说明。砍完要用同一评测集回归。
- **缓存会不会用脏结果？** 按工具参数做键，写操作与带 TTL 的读分开；失效要可强制刷新。
- **和上下文窗口爆了是同一题吗？** 相关但不全同。窗口爆了会截断；本题是账单和延迟，即使没截断也会贵。见 `pdd-context-overflow`。窗口没爆但每轮多 10k observation，费用也会快速增加。
