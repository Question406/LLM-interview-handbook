---
id: drustz-7feaf5bdda2157a04d
section: research
order: 140
level: A
title: OpenAI 最高频编码题：病毒/感染网格模拟（Rotting Oranges 994 强化版，5 段渐进 follow-up）
quick: >-
  supplemental-research-note · OpenAI 最高频编码题：病毒/感染网格模拟（Rotting Oranges 994 强化版，5
  段渐进 follow-up）
companies:
  - openai
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.reddit.com/r/leetcode/comments/1qsca8h/openai_phone_screen_question/
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

三个独立来源（2026-01 r/leetcode 店面实拍帖被版主删但评论存活、PichupOrg 完整题面、2026-07 onsite 面经'Virus Spread in a Storage Room'）确认这是店面+onsite 都在用的高频题。完整 5 部分：P1 基础感染——X 感染 8 邻域（或4邻域变体），每天一轮，返回稳定所需天数（多源 BFS，答案=最后一层深度）；P2 加免疫植物 'I'（永不感染、阻挡传播）——好的 P1 抽象应一行改完；P3 感染 D 天后恢复为 '.' 且可再感染——层数计数失效，改事件驱动模拟（按恢复日 keyed 的优先队列 + 每日 frontier），小 D 可能振荡，需 maxDays 上限+重复状态检测并主动说出来；P4 死亡条件——恢复时若 ≥K 个感染邻居则死亡变 'D'（永久墙）；P5 开放优化——每天开始可烧掉一行/列作永久防火带，最小化总死亡数：无闭式解，要给可辩护的启发式（贪心烧感染最多的线）+说明其局限。评分 rubric：核心算法（多源 BFS vs 每天重扫）、可扩展性（cell 类型与步进逻辑分离）、事件建模、边界（全免疫/再感染/振荡）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.reddit.com/r/leetcode/comments/1qsca8h/openai_phone_screen_question/)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
