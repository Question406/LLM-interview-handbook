---
id: drustz-50adcbe291c582e527
section: forum-notes
order: 261
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Examples
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Examples
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
## Examples

Example 1:

Input: `limit = 2, shards = ["A:0:100", "B:40:110", "C:80:200", "D:210:300"]`

Output: `["A:0:100", "B:40:110", "C:101:209", "D:210:300"]`

Explanation:

Shard `C` cannot start at `80` because keys `80..100` are already covered by `A` and `B`. It shifts to `101`. Then `C` is extended to `209` to fill the gap before `D`.

Example 2:

Input: `limit = 1, shards = ["A:0:100", "B:80:180"]`

Output: `["A:0:100", "B:101:180"]`

Example 3:

Input: `limit = 2, shards = ["A:0:30", "B:0:31", "C:0:32", "D:0:100"]`

Output: `["A:0:30", "B:0:31", "C:31:32", "D:32:100"]`

Explanation:

After `A` and `B`, shard `C` must move to `31`. Shard `D` is processed later and must start after the saturated region, so it becomes `32:100`.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
