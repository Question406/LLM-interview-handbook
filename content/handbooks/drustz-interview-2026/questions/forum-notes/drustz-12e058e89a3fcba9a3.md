---
id: drustz-12e058e89a3fcba9a3
section: forum-notes
order: 239
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Next Steps
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Next Steps
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
## Next Steps

If you want to practice even harder versions (Level 4 or 5), consider these ideas:

- **Level 4:** What if `N > 1`? A person needs 2 or 3 sick neighbors to get infected.
- **Level 5:** Multiple virus types competing for space.

### Testing Your Code

Here are some tests to make sure your code works:

```python
# Test 1: Basic center infection
assert time_to_full_infection([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2

# Test 2: Corner infections
assert time_to_full_infection([[1, 0, 0], [0, 0, 0], [0, 0, 1]]) == 2

# Test 3: No infection source
assert time_to_full_infection([[0, 0], [0, 0]]) == -1

# Test 4: Already fully infected
assert time_to_full_infection([[1, 1], [1, 1]]) == 0

# Test 5: Single cell
assert time_to_full_infection([[1]]) == 0
assert time_to_full_infection([[0]]) == -1

# Test 6: Linear spread (a line)
assert time_to_full_infection([[1, 0, 0, 0, 0]]) == 4

# Test 7: Larger grid
grid = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
]
assert time_to_full_infection(grid) == 4
```



*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100132*)

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
