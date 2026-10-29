---
id: drustz-ededf9d8e869f0e7e3
section: forum-notes
order: 286
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 4: Making It Faster (Follow-up)'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 4: Making It Faster (Follow-up)'
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
## Part 4: Making It Faster (Follow-up)

**Interviewer Question**: "How can we make this faster or use less memory?"

### Current Performance

**Time Complexity**:

- `__next__`: O(1) (constant time per step).
- Total for N addresses: O(N).
**Space Complexity**: O(1) (we only store the current state).

### Ways to Improve

- **Skip Steps**: If you want to jump through IPs (like every 100th one), add a `step` parameter.

```python
def __init__(self, ip_cidr: str, reverse: bool = False, step: int = 1):
    self.step = step


def __next__(self):
    # ...
    self.current += self.step  # instead of += 1
```



- **Batch Operations**: Return a list of IPs at once instead of one by one. This is faster for large data processing.

```python
def next_batch(self, size: int) -> list[str]:
    batch = []
    for _ in range(size):
        try:
            batch.append(next(self))
        except StopIteration:
            break
    return batch
```



- **Memory**: If you create many iterators, cache the CIDR calculations so you don't redo the math for the same network.

### Discussion Points

- **Int vs String**: Storing the IP as an integer is efficient (only 32 bits). Storing it as a string is slow and uses more memory.
- **Vectorization**: If you need to process millions of IPs, libraries like NumPy are faster than standard Python loops.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
