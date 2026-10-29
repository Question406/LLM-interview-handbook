---
id: drustz-40edc7c9178c5e34b8
section: anthropic
order: 32
level: A
title: Coding Bootloader
quick: locally-saved-same-problem-prompt-and-hints · Coding Bootloader
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-same-problem-prompt-and-hints
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
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-bootloader
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Repair Bootloader Program

A [bootloader](https://en.wikipedia.org/wiki/Bootloader) stores its program as an array of text instructions, and you need to find where the execution first starts repeating.

You are given `instructions`, where each entry has the form `"<operation> <value>"`. The operation is one of `"plus"`, `"next"`, or `"jump"`.

- `"plus x"` adds `x` to a global accumulator, then moves to the next instruction.
- `next x` leaves the accumulator unchanged and moves to the next instruction. The value `x` is preserved in the instruction format but is **ignored** and not used in this question.
- `"jump x"` leaves the accumulator unchanged, then moves to the instruction at the current index plus `x`.

### Part 1：本地保存的提示与追问

#### 核心目标
- Simulate a simple instruction sequence starting from index zero.
- Track executed instruction indices to identify when execution revisits a previous step.
- Return the index of the first repeated instruction, or -1 if the program terminates normally.

#### 解题提示
- Maintain a record of every instruction index you visit during the simulation.
- Check for repetition immediately before executing the current instruction rather than after.
- Use a boolean array or hash set to achieve O(1) lookups for visited indices, ensuring overall O(N) runtime.

#### 常见追问
- How would you adapt this approach if the instruction set included conditional jumps?
- Can you reduce the space complexity while still detecting the cycle efficiently?
- What happens if the jump offset causes the program counter to go out of bounds?
- How does this problem conceptually map to cycle detection in a functional graph?

#### 考察点
- Program simulation and state management
- Cycle detection in deterministic sequences
- Efficient lookup structures for visited states
- Control flow manipulation via program counter

### Part 2：本地保存的提示与追问

#### 核心目标
- Simulate a simple bootloader program that may contain exactly one invalid branch instruction.
- Identify and flip at most one jump or next instruction to guarantee normal termination.
- Return the final accumulator value after applying the minimal necessary correction.

#### 解题提示
- Model each instruction as a node in a directed graph where edges represent control flow; a non-terminating run indicates a cycle.
- Instead of testing every possible flip, simulate the original execution path and focus only on branch instructions encountered during that run.
- Precompute which nodes can reach the terminal state by traversing backward from the end, enabling O(1) validation of whether flipping a specific instruction fixes the loop.

#### 常见追问
- How would you adapt this approach if multiple instructions could potentially be flipped?
- Can the reverse graph be avoided by using only forward simulation and visited tracking?
- What is the time and space trade-off if we validate each potential flip independently?
- How would you handle cases where the program terminates immediately without any jumps?

#### 考察点
- Graph reachability and cycle detection in execution traces
- State machine simulation with controlled modifications
- Reverse traversal to precompute termination paths
- Efficient validation of candidate corrections

---

### 用户本地练习实现（已通过对应单元测试）

- practice/anthropic/bootloader_repair.py
- 测试：tests/test_bootloader_repair.py

### 来源与内容类型

- Content kind: `locally-saved-same-problem-prompt-and-hints`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-bootloader)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
