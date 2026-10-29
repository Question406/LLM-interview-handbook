---
id: drustz-8bf30ff21c9a70b109
section: research
order: 8
level: A
title: Anthropic 55分钟 live 技术店面（CodeSignal notebook）真题：图像处理管线（Pillow + JSON 配置）
quick: >-
  supplemental-research-note · Anthropic 55分钟 live 技术店面（CodeSignal
  notebook）真题：图像处理管线（Pillow + JSON 配置）
companies:
  - anthropic
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
      https://www.reddit.com/r/OfferEngineering/comments/1ub6od5/anthropic_frontend_phone_screen_not_leetcode_but/
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

多个独立报告的高频店面题（前端/后端/senior 都有人抽到）：给一组图片和一个 JSON 定义的 pipelines 列表，每个 pipeline 含变换序列（转黑白、resize、水平翻转等），实现主函数把每张图按其 pipeline 顺序处理并导出。需要现场选图像库（Python 基本只能 Pillow）、快速读文档、把每种变换映射到库调用。Follow-up：图片变大后的性能优化——判断 I/O-bound vs CPU-bound；I/O: 流式读取/批量文件操作；CPU: 跨图片并行（进程池）、避免重复变换。环境是 Jupyter 式 notebook、无自动补全、可 Google（不能点 AI 摘要）、禁 AI。一人用 Java 被允许但 Pillow 题基本锁 Python。有人因此挂掉，有人过（评论：'每一步都能 google，不难但时间极紧，一个错误选择就完了'）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.reddit.com/r/OfferEngineering/comments/1ub6od5/anthropic_frontend_phone_screen_not_leetcode_but/)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
