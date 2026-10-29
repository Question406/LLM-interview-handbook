---
id: drustz-bcbe26d34ae9a0a47c
section: research
order: 147
level: A
title: 感染/传染病模拟（infection spread）2026年6-7月仍为电面+onsite最高频题，新增免疫/动态免疫/死亡阈值 follow-up
quick: >-
  supplemental-research-note · 感染/传染病模拟（infection
  spread）2026年6-7月仍为电面+onsite最高频题，新增免疫/动态免疫/死亡阈值 follow-up
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
    url: 'https://www.1point3acres.com/bbs/thread-1181047-1-1.html'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

多个 2026 年 6 月帖确认：thread-1181047（2026-06-23，tech screen）：类似 LC994 腐烂橘子，分部：Part1 几乎 994 原题（多源 BFS 逐天扩散）；Part2 识别'免疫'的 unit；Part3 动态免疫——被感染 x 天之后的 unit 会变免疫，此时不能再用普通 BFS（需逐天模拟+状态机）。楼主止步 Part3。thread-1181839（2026-07-01 过经）：onsite coding 是 infection，共做出 5 问。thread-1180717（2026-06-19）：电面第一轮是传染病，'真的要练熟，不然很多 followup 写不完'。thread-1180678（2026-06-19）：onsite 含'植物感染'。thread-1180670：电面两题之一是'植物'。thread-1181079（2026-06-23）：病毒传播+国际象棋。1p3a 官方题库显示该题 last asked 2026-06-29，频率 Very High，60 分钟 5 个 sub-part 递进。PracHub 2026-06-20 上报变体'Infection Spread Simulation with Death Threshold'（m×n grid，离散天数同时更新，加死亡阈值规则）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/bbs/thread-1181047-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
