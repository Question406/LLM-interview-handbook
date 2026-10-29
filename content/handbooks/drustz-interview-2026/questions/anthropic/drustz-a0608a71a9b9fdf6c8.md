---
id: drustz-a0608a71a9b9fdf6c8
section: anthropic
order: 12
level: A
title: Coding Q3 Stack Trace
quick: locally-saved-topic-editorial · Coding Q3 Stack Trace
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q3-stack-trace
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Converting Stack Samples to Trace Events

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

## System Design Discussion

These questions are for verbal discussion. You do not need to write code, but you should be ready to explain your logic.

### Comparing from Top vs. Bottom

**Question:** The basic solution compares stacks from the top down (Prefix). How is comparing from the bottom up (Postfix/Suffix) different, and why might it be better for profiling?

**Discussion Points:**

**Prefix Comparison (Top-Down)**:

- Compares starting from the root (e.g., "main").
- If the top layers match, it treats them as the same call chain.
- **Problem:** This is not very detailed. It might group different leaf functions together if the top layers look the same.
- Top-level functions usually change less often, so this method misses small details.
**Postfix Comparison (Bottom-Up)**:

- Compares starting from the leaf (the deepest function).
- It looks for the deepest parts of the stack that are different.
- **Benefit:** This is more accurate for profiling. The leaf function is where the work actually happens, and it changes the most.
**Example**:

```text
Stack A: main → handler → parse → foo
Stack B: main → handler → parse → bar
```



- **Prefix comparison**: The first 3 layers match. It might treat these as the same event.
- **Postfix comparison**: The leaves ("foo" vs "bar") are different. This clearly shows that the activity changed.
**Why This Matters**: In profiling, we want to know exactly which leaf function is running. Postfix comparison helps by:

- Distinguishing between different paths of execution.
- Better identifying "hot spots" (functions using the most resources).
- Reducing noise by focusing on real changes at the bottom of the stack.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100016*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q3-stack-trace)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
