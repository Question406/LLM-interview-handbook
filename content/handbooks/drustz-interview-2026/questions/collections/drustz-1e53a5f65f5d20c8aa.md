---
id: drustz-1e53a5f65f5d20c8aa
section: collections
order: 47
level: A
title: 通用 ML 理论 + ML System Design 资源库 · Coding 题
quick: 作者文档章节 · 通用 ML 理论 + ML System Design 资源库 · Coding 题
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md
    type: primary
---
## Coding 题

### Google OA/Coding: Maximize Coins Collection (token 每次右移3格, 完整题干)
*medium · 频率: single report · 2025-11*

岗位: Google 2026 SWE Online Assessment (通过 1p3a interview OJ API 取到完整公开题干, tid 1157978)。题目: 给一个一维棋盘字符串(长度<=100), 字符为 '.'(空)、'T'(玩家 token)、'C'(硬币)。玩家可移动多个 token, 每个 token 每步严格向右移动 3 格, 不能左移也不能移动其他步数; 若目标格被另一 token 占用则该移动非法。硬币只有在 token 落在其上时才被收集(路过不算)。求最多能收集多少硬币。样例输入: '...TC.TC.' / 'TT.CCCC.T' / 'C..T..C..TT..' / '....T...T...C' / 'TTT.'。虽为通用 Google OA, 但可能出现在 GDM RE coding 轮。

**解法**: 解法: 每个格子按 index mod 3 分成 3 条独立链(因每步 +3, token 只在同余类内移动)。在每条链上把格子重排为一维序列, 问题变为: 若干 token 沿链向右逐格移动(不可越过/占用同格), 每落点若是 C 则 +1, 最大化收集数。链内用 DP/贪心处理 token 与 coin 的匹配(注意占用冲突: 两 token 不能同格, 靠右 token 先动或按顺序 DP)。总复杂度 O(n)。

来源: &lt;[来源链接](https://www.1point3acres.com/interview/thread/1158159&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/theory-and-mlsd.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md)。作者整理资料；许可和第三方来源范围见阅读指南。
