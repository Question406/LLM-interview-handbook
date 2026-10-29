---
id: drustz-68cadf12fd32681e20
section: openai
order: 169
level: A
title: Maximize The Hits
quick: original-structured-preparation-guide · Maximize The Hits
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
    url: 'https://www.1point3acres.com/interview/problems/openai-maximize-the-hits'
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Maximize The Hits

> 公开资料没有完整约束，而且“穿墙成本是否还要额外加普通移动成本”并不完全明确。下面把假设写清楚，不能视为已确认的官方标准解。

## 可确认的题意模型

角色从整数坐标 `0` 出发，墙位于相邻整数位置之间，也就是半整数位置。普通移动消耗能量；穿过一面墙还会产生与墙厚相关的能量消耗，并获得一次 hit。墙不会消失，所以可以来回穿越同一面墙。在总能量不超过 `E` 的条件下，最大化 hit 数。

## 动态规划

先采用以下明确假设：

- 无墙边的移动成本为 `1`，收益为 `0`；
- 有墙边的总成本为墙厚 `thickness`，收益为 `1`；
- 所有成本至少为 `1`。

定义：

```text
dp[e][x] = 恰好使用 e 点能量到达位置 x 时，最多获得多少 hit
```



从 `dp[0][0] = 0` 开始，向左右相邻位置转移：

```text
dp[e + cost(x,y)][y] = max(
    dp[e + cost(x,y)][y],
    dp[e][x] + reward(x,y)
)
```



虽然物理路径可以来回走，但每次转移的能量都严格增加，因此按能量从小到大计算不会形成 DP 环。答案是所有 `e <= E` 和所有位置中的最大值。

## 复杂度

能量为 `E` 时，可达整数位置最多约 `2E + 1` 个，因此时间和空间上界都是 `O(E²)`。这是依赖能量数值的伪多项式算法。

## 必须向面试官确认

- 穿墙成本是替代普通移动成本，还是 `1 + thickness`；
- 墙厚能否为 0；
- 同一条边能否有多面墙；
- `E` 是否很大，大到不能使用 `O(E²)`；
- 起点附近之外是否存在有限的墙坐标范围。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/openai-maximize-the-hits)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
