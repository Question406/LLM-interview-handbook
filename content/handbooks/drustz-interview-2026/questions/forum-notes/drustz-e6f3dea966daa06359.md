---
id: drustz-e6f3dea966daa06359
section: forum-notes
order: 295
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Speed and Memory Usage
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Speed and Memory Usage
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Speed and Memory Usage

### Basic Implementation (Part 1)

- **setCell()**: **O(1)**. It is very fast because we just save the text.
- **getCell()**: **O(N)**. It is slow. We might have to check every cell in the chain.
- **Memory**: **O(K)**, where K is the number of cells.

### Optimized Implementation (Part 2)

- **setCell()**: **O(D)**. Slower than before. We have to update D cells that depend on the changed cell.
- **getCell()**: **O(1)**. Extremely fast. We just read the saved answer.
- **Memory**: **O(K + E)**. We use more memory to store the connections (edges) between cells.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
