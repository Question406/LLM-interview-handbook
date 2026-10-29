---
id: drustz-4bb6b9a0aa165897f5
section: openai
order: 46
level: A
title: Maximum Falling Path with Limited Vertical Jumps and Bonus Scoring
quick: >-
  original-structured-preparation-guide · Maximum Falling Path with Limited
  Vertical Jumps and Bonus Scoring
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
    url: >-
      https://www.1point3acres.com/interview/problems/9783914a-7d86-5a41-94e1-af1b1f9fb063
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Maximum Falling Path：有限跳跃与 Bonus

> 公开 OJ 描述已与当前 UUID 精确对应；旧正文只是低频题目清单，现已移除。下面是公开题意的中文重述和原创解法。

## 题目要做什么

给定 `N × M` 整数矩阵，从第一行指定位置 `(0,p)` 出发到达最后一行：

- 普通移动可到左下、正下、右下；
- 最多 `K` 次可以同列向下跳两行；
- 路径基础分是访问格子的数值总和；
- 相邻两次落点的值相同，额外加 `X`；
- 连续三个落点的值严格递增，额外加 `Y`。

需要输出最大分数、一条最优路径，以及最优路径数量对 `1_000_000_007` 取模。公开约束为 `N,M ≤ 200`。

## DP 状态

奖励依赖最近三个落点，所以状态必须保留“前一个格子”和“当前格子”，不能只记录当前坐标：

```text
state = (previous_cell u, current_cell v, jumps_used k)
```



从 `v` 转移到合法下一格 `w` 时：

```text
gain = board[w]
if board[v] == board[w]: gain += X
if u exists and board[u] < board[v] < board[w]: gain += Y
```



每个状态保存三项：最大分数、达到该分数的路径数、任意一个父状态。更高分时覆盖三项；同分时累加路径数，但父状态保留一个即可用于恢复示例路径。最终汇总所有当前格位于最后一行且 `k ≤ K` 的状态。

由于每个格子的合法前驱只有常数个，虽然状态写了两个相邻格子，总状态量仍是 `O(NMK)`。不可达状态设为负无穷，避免全负矩阵被错误地从中途开始。

## 复杂度

时间和保存全部父指针的空间都是 `O(NMK)`。若只求分数与计数，可滚动保存必要行；但恢复路径仍需父指针或第二次回溯计算。

## 边界

单行矩阵、`K=0`、全部负分、跳两行越过最后一行、相等 bonus 与递增 bonus 是否可同时触发、多个最优终态的计数，以及路径数取模但分数不能取模。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/9783914a-7d86-5a41-94e1-af1b1f9fb063)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
