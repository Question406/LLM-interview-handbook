---
id: byte-token-cost-debug
section: systems
order: 200
level: A
title: 字节秋招一面：Agent Token 涨得太快，怎么定位和压？
quick: >-
  先按 turn
  记账：system、工具字段和类型规范（schema）、检索回写、历史各占多少。先砍重复的工具回传和没压缩的日志，再缩小候选工具，最后才换小模型。定位靠每一步的
  token 记录，别先去改温度。
tags:
  - ByteDance
  - Token Cost
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 字节AI Agent开发秋招一面面经
    url: 'https://www.nowcoder.com/feed/main/detail/7b1b40fda3244715a82bcb4a821ca887'
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：AI Agent 开发；秋招一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“如果发现 Agent 运行过程中 Token 消耗增长过快，会如何定位问题并进行优化？”**

我会先按 turn 建一本 token 账，看 system、工具字段和类型规范（schema）、检索回写、历史、completion 各占多少，找到占比最大的那一类再压。压的顺序是结构化抽取 → 渐进披露工具 → 三级压缩 → 缓存幂等读，换小模型放在最后。先改温度或者先换模型，都是在没定位的情况下乱动。

常见的元凶就那几个：整页 JSON 回灌、全量工具目录、压缩没开、循环重试。典型的账是这样的：第 1 轮 8k，第 8 轮 80k，每一轮都把 `pytest -q` 的二十页日志和四十个工具 schema 原样塞回去。这类问题多出现在多轮、工具返回大、历史越来越长的场景；单轮短问答的 token 涨了，更可能是定价变了或者出现了重试风暴。

定位的做法是每一步记录各类 token 数，画堆叠图看哪一类占比最大。改一类，复测一类，别同时动温度、模型和压缩；定位没做完之前，也不要同时开压缩又换模型。账本按 request id 落盘，事后才能证明是 schema 膨胀还是 observation 膨胀，不用凭感觉去砍 prompt。

压的时候，先对日志和检索结果做失败栈或字段抽取，只留相关的几十行。工具按当前阶段渐进披露，比如编码阶段只暴露 `read_file` / `run_test` / `apply_patch`。历史用近几轮原文加中期摘要。幂等读的结果做缓存，免得同一个 URL 每轮都回灌一次。三级压缩（近轮原文、中期摘要、远期丢弃）要写成固定策略，别每次让模型自己决定留什么。换小模型放在最后，因为它同时改了质量和价格，会把实验搅浑。

最后要回归，「降本」和「丢约束」得分开验收。只砍长度、不看任务成功率是危险的：关键的 Observation 被砍掉以后，模型更爱重试，token 不降还升。所以压缩前后要对一份硬约束清单，路径、测试命令、禁止改的文件、失败用例名、断言都还得在，否则省下的 token 会变成更多轮的重试，总成本更高。线上按成分告警：schema 占比、observation 占比、重试轮次。循环重试要设轮次预算和同类错误熔断，不然压缩省下来的 token 会被死循环吃回去。整体顺序就是：账本 → 砍回写 → 缩工具面 → 摘要历史 → 最后才动模型。

## 追问

**怎么证明定位对了？**
堆叠图上改动的那一类明显下降，任务成功率也没掉。一次只改一类 token，因果才说得清。

**system prompt 能不能一起砍？**
可以做版本化精简，但安全和 schema 约束优先，文字说明可以先删。砍完用同一个评测集回归。

**缓存会不会返回脏结果？**
按工具参数做键，写操作和带 TTL 的读分开，失效要能强制刷新。

**这和上下文窗口爆了是同一道题吗？**
相关，但不完全一样。窗口爆了会截断；这题说的是账单和延迟，就算没截断也会贵。窗口没爆、但每轮多出 10k observation，费用一样涨得很快，见 `pdd-context-overflow`。

相关：`byte-three-level-compress`、`xiaohongshu-mcp-skill-token-efficiency`
