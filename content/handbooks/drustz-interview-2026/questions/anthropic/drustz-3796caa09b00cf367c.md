---
id: drustz-3796caa09b00cf367c
section: anthropic
order: 78
level: A
title: Infection Simulation in a Grid
quick: original-structured-preparation-guide · Infection Simulation in a Grid
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/60cdb5a8-ed94-46ca-9d0c-3198b18f62cb
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Infection Simulation：需要至少 N 个感染邻居

## 证据边界与完整题面

公开 description 给出：输入 `n,m`、由 `H`/`I` 构成的网格和阈值 `N`。每个健康格若在某天开始时有至少 `N` 个上、下、左、右感染邻居，则下一天变为感染；感染永久存在，更新必须同步。实现 `time_to_full_infection(rows,N) -> int`，全部感染返回所需轮数，稳定后仍有 `H` 返回 `-1`。

自洽例子：`["II","IH"]` 且 `N=2`，右下格有上方和左方两个感染邻居，第 1 天感染，答案 1。公开页的 3×3、两对角感染源、`N=2` 样例写 3；在其文字指定的 4 邻域下第一天无人达阈值，应为 `-1`，因此必须向面试官确认样例是否暗示 8 邻域或不同计时，而不能同时宣称两套规则都正确。

## 单调计数优化

感染只增不减，所以为每个健康格维护 `infected_neighbor_count`。先让全部初始感染格贡献一次计数，把达到 `N` 的健康格安排到 day 1；随后按 day 分层处理新感染格，它只给最多四个仍健康邻居加一，某格第一次达到阈值时安排到下一天并立刻标记为 scheduled，防止重复。剩余健康数归零时返回当前 day，否则队列空即 `-1`。

每条网格邻接边只处理常数次，时间 `O(nm)`、计数和队列空间 `O(nm)`，比每轮全表重扫的最坏 `O(Tnm)` 更稳。测试 `N=1`、`N>4`、`N<=0` 的合同、全 I、全 H、多格同日达到阈值、细长网格和同步更新。该页确认 **4 邻域与阈值 N**；8 邻域、空地、免疫、康复、死亡均未确认。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/60cdb5a8-ed94-46ca-9d0c-3198b18f62cb)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
