---
id: drustz-ad1612fb56e9eb6cd8
section: forum-notes
order: 152
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Follow-up Question: Reducing Noise'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Follow-up Question: Reducing Noise'
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Follow-up Question: Reducing Noise

Sometimes fast functions appear for a very short time and clutter the data. Modify your code to only create start/end events if a function appears in **N samples in a row** (N is a number you can set).

### Defining a Streak

A function is "consecutive" only if the **exact same frame** (same depth and parent functions) appears N times in a row.

**Important:** If a function stops and then starts again later, the counter resets. You cannot add the two separate appearances together.

### Debouncing Example (N = 2)

**Input samples**:

```text
t=1.0: ["main"]
t=2.0: ["main"]
t=3.0: ["main", "foo"]
t=4.0: ["main", "foo"]
```



**Expected output**:

```text
start 2.0 main     # main appeared in 2 samples, so it is confirmed
start 4.0 foo      # foo appeared in 2 samples, so it is confirmed
```



### Edge Case Warning

Look at these samples:

```python
Sample(1, ['a', 'b'])
Sample(2, ['a', 'b', 'c'])
```



Here, `a` and `b` are consecutive because they are in the same position in both lists.

However, in this case:

```python
Sample(1, ['a', 'b'])
Sample(2, ['c', 'b', 'a'])
```



Here, `a` and `b` do **NOT** count as consecutive. At t=2, the stack changed completely. The frames `a` and `b` from t=1 must close before the new stack starts. Even though the names are the same, the call path is different.

### Function Signature

```java
List<Event> convertSamplesToDebouncedEvents(List<Sample> samples, int N)
```



### Important Hints

- You can mark the start time at the 1st sample or the Nth sample (either is fine if you are consistent).
- Focus on tracking the streak correctly. Any interruption resets the count to zero.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
