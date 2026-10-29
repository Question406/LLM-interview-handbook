---
id: drustz-d2bf1ed7d334b81f43
section: forum-notes
order: 151
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Problem Statement
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Problem Statement
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
## Problem Statement

A sampling profiler takes a snapshot of the active call stack at specific times. You get a list of these snapshots (samples), sorted by time. Each sample has:

```cpp
struct Sample {
    double ts;                      // timestamp
    std::vector<std::string> stack; // call stack (outermost → innermost)
};
```



Your job is to turn these samples into a timeline of events. You need to create a list showing when functions started and ended:

```cpp
struct Event {
    std::string kind;   // "start" or "end"
    double ts;          // timestamp
    std::string name;   // function name
};
```



### Example Scenario

**Input samples** (sorted by time):

```text
t=1.0: ["main"]
t=2.5: ["main", "func1"]
t=3.1: ["main"]
```



**Expected output**:

```text
start 1.0 main
start 2.5 func1
end   3.1 func1
```



### Key Rules

- **Sorted Input:** The samples come in the correct time order.
- **Find Changes:** Look at two samples side-by-side to see what is different:

Create **End events** for functions that are no longer there (remove from the bottom up).
- Create **Start events** for new functions (add from the top down).
- **No Auto-Closing:** Do not create "end" events for functions remaining after the very last sample.
- **Handle Recursion:** If the same function name appears at different depths in the stack, treat them as separate frames.

### Function Signature

```java
List<Event> convertSamplesToEvents(List<Sample> samples)
```



### Important Hints

- The stack list goes from the root (like "main") down to the leaf (the function running right now).
- To decide what started or ended, find the longest shared starting part (prefix) of the two consecutive stacks.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
