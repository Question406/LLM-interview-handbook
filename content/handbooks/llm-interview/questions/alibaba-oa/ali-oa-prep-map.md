---
id: ali-oa-prep-map
section: alibaba-oa
order: 1
level: S
title: 阿里校招笔试 / 研发面应该按哪几条线刷？
quick: >-
  机试按变形刷：环形、不相邻、贪心构造、区间调度、数位和方差维护；手撕抓链表、DP、LRU；研发面再补 JVM/Redis/MQ/MySQL 和「流量 ×100」。LLM 算法题用「按公司」筛阿里。
tags:
  - Alibaba
  - 备考地图
  - 笔试
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
---

这张卡是阿里校招笔试和研发面的备考地图，按四条线刷：先过机试编程的变形题，再补 AI 笔试的选择和 Prompt，然后练技术面手撕，后端岗最后加研发八股。每条线下面列的是本手册的题卡 id，本页只给地图。

近年公开场次的结构大致稳定：选择（CS + 近年 AI）加 2 到 3 道编程，AI 研发还会多 1 道 Prompt。编程爱在经典算法上加约束，很少原题照搬，所以按力扣题号顺序刷收效不大；LLM 人才计划的 GRPO / Agent 题也别和本章机试卡混成一套背诵。

## 线 1：机试变形（先过编程）

代表场次是淘天 / 国际实习、淘天算法 0816、淘天研发 0411、春招 0401。按题型刷，别按日期刷：

- 环形 / 不相邻：`ali-oa-ring-lights`、`ali-oa-nonadj-even`
- 贪心构造 / 区间：`ali-oa-gems`、`ali-oa-rescue`、`ali-oa-k-residue`、`ali-oa-max-common-subseq`
- 数位 / 模运算：`ali-oa-picky-eater`、`ali-oa-mod3-concat`、`ali-oa-mod-cycle`、`ali-oa-hex-popcount`、`ali-oa-nearest-prime`
- 维护结构：`ali-oa-variance`（树状数组维护区间方差）、`ali-oa-jam`、`ali-oa-reverse-seq`
- 模拟 / 压缩：`ali-oa-match3`、`ali-oa-color-ops`、`ali-oa-bin-compress`、`ali-oa-k-repeat-substr`、`ali-oa-perm-subseq`、`ali-oa-spotlight`、`ali-oa-candy`

每天闭卷复述 1 道，讲清「状态 / 贪心不变量 / 会炸的边界」，别对着题解抄。

## 线 2：AI 笔试选择 + Prompt

0325 AI 研发场考了三块：`ali-oa-ai-mcq`（Teacher forcing / GQA / ReAct / MCP）、`ali-oa-taxi-prompt`（把规则写成可过的提示词）、`ali-oa-cs-mcq`（TCP、Best Fit、GROUP BY、锁）。概念题点到为止，要展开就回 `code-gqa` 和 Agent 章，这条线上不用默写整套公式。

## 线 3：技术面手撕

链表 + DP + LRU 是门槛，清单见 `ali-algo-prep-list`。必刷卡是 `ali-algo-list-family`、`ali-algo-edit-distance`、`ali-algo-kth-largest`、`ali-algo-level-order`、`ali-algo-lru`，写完接着练 `ali-algo-scale-100x`。

## 线 4：研发八股（Java / 后端岗）

`ali-be-jvm-gc`、`ali-be-thread-lock`、`ali-be-hashmap`、`ali-be-spring`、`ali-be-redis`、`ali-be-mq`、`ali-be-mysql-mvcc`、`ali-be-mysql-index`、`ali-be-rate-limit`、`ali-be-seckill`、`ali-be-tcc`、`ali-be-shard-id`、`ali-be-shorturl-redpacket`。每张卡都用「淘天场景 + 流量 $\times 100$」收口，别背定义列表。

LLM 人才计划的 GRPO / Agent / Skill 回 `fund-pg-ppo-grpo-index`、`agent-skill-eval` 去看，别和本章机试卡混着背。

## 追问

**四条线要并行吗？**
不用。机试前两周只走线 1，出成绩后加线 3，后端岗再加线 4；AI 岗把线 2 和 LLM 章插在晚上。

**为什么不按场次日期刷？**
同一种变形会换皮重考，按题型刷才能迁移。

**Prompt 题算算法题吗？**
不算。它考的是规则覆盖和可执行约束，见 `ali-oa-taxi-prompt`。
