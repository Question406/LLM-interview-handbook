---
id: drustz-28573ce0e8d191eacb
section: research
order: 165
level: A
title: >-
  Research Engineer 高难轮（Exponent 详细复盘）：分布式 all_gather + 噪声信道误差界推导；transformer
  四区域找 bug + KV cache
quick: >-
  supplemental-research-note · Research Engineer 高难轮（Exponent 详细复盘）：分布式
  all_gather + 噪声信道误差界推导；transformer 四区域找 bug + KV cache
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
      https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Exponent 上的 RE 面经（约 2025 年中，7 周流程，技术轮后被拒）：(1) 最难轮（ML statistics/information theory）：实现多节点 all_gather → 信道有噪声时推导达到目标误差所需轮数的 worst-case 公式 → naive bound 太慢如何改进 → 利用'传的是 float 而非任意实数'设计更优算法（利用浮点表示的有限性）。研究生级信息论，面试官几乎不给提示。(2) ML debugging 轮：transformer 实现有四个标注区域各藏一个 bug，逐一找出；然后实现 KV caching 并讨论需要改哪些部分和进一步优化。(3) 算法轮：'给一个 Python package，找支持它的最新 Python 版本'——分层二分查找（对应已知 version dependency 题）。(4) 手速轮：乐器 beat string → 乐谱记法转换，扩展多乐器、建模休止符（对应 interviewdb 'Beat Notations'）。(5) 系统轮：KV store serializer/deserializer + 关机后持久化恢复 + 关机状态下的查询处理。总体评价：比 FAANG 少提示、不可套路（'less gameable'）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
