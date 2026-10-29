---
id: drustz-fbe61c3a01873c26e4
section: research
order: 49
level: A
title: 'String Tokenization (Trie, longest-match)'
quick: 'supplemental-research-note · String Tokenization (Trie, longest-match)'
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6941b6aeb9d646bec48c68b7
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开题面或公开解法。

Stage: phone screen. Given `text` and `dictionary` of strings "&lt;key&gt;:&lt;id&gt;". Segment text into tokens: (1) Longest Match Priority - at each position pick the longest dictionary key matching there; (2) Greedy Consumption - consume the matched token, continue from next unconsumed char; (3) Literal Preservation - if nothing matches, emit the single char as a literal token; (4) Output the id for matched keys, the char itself otherwise. Constraints: 1<=text.length<=1e9, 0<=dictionary.length<=1e9, tokens unique. Examples: text="applepiepear", dict=["app:10","apple:20","pie:30"] -> ["20","30","p","e","a","r"]; "acdebe",["a:1","b:2","cd:3"]->["1","3","e","2","e"]; "programmingprogrampropro" with pro/program/programming/gram/ming/pr/og -> ["3","2","1","1"]. 8 official test cases captured incl. empty text, empty dict, "thetheatertheme". Site follow-ups: dictionary too large to fit / stored externally; fuzzy or partial matching; space optimization when keys share prefixes. Acceptance rate on site: 36.6%.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6941b6aeb9d646bec48c68b7)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
