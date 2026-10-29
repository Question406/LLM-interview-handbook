---
id: drustz-58ce75d17e38bae6fb
section: collections
order: 36
level: A
title: hack2hire 完整题解（抓取的解锁内容） · Repair Bootloader Program
quick: 作者文档章节 · hack2hire 完整题解（抓取的解锁内容） · Repair Bootloader Program
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/hack2hire-premium.md
    type: primary
---
## Repair Bootloader Program

### Part 1
A [bootloader](https://en.wikipedia.org/wiki/Bootloader) stores its program as an array of text instructions, and you need to find where the execution first starts repeating.

You are given `instructions`, where each entry has the form `"<operation> <value>"`. The operation is one of `"plus"`, `"next"`, or `"jump"`.

- `"plus x"` adds `x` to a global accumulator, then moves to the next instruction.
- `next x` leaves the accumulator unchanged and moves to the next instruction. The value `x` is preserved in the instruction format but is **ignored** and not used in this question. 
- `"jump x"` leaves the accumulator unchanged, then moves to the instruction at the current index plus `x`.

**概要**:
- Simulate a simple instruction sequence starting from index zero.
- Track executed instruction indices to identify when execution revisits a previous step.
- Return the index of the first repeated instruction, or -1 if the program terminates normally.

**考察点**:
- Program simulation and state management
- Cycle detection in deterministic sequences
- Efficient lookup structures for visited states
- Control flow manipulation via program counter

**常用模式**:
- Simulation
- Hashing

**提示**:
- Maintain a record of every instruction index you visit during the simulation.
- Check for repetition immediately before executing the current instruction rather than after.
- Use a boolean array or hash set to achieve O(1) lookups for visited indices, ensuring overall O(N) runtime.

**可能的 follow-up**:
- How would you adapt this approach if the instruction set included conditional jumps?
- Can you reduce the space complexity while still detecting the cycle efficiently?
- What happens if the jump offset causes the program counter to go out of bounds?
- How does this problem conceptually map to cycle detection in a functional graph?

### Part 2
A [bootloader](https://en.wikipedia.org/wiki/Bootloader) stores its program as an array of text instructions, and you need to find where the execution first starts repeating.

You are given `instructions`, where each entry has the form `"<operation> <value>"`. The operation is one of `"plus"`, `"next"`, or `"jump"`.

- `"plus x"` adds `x` to a global accumulator, then moves to the next instruction.
- `next x` leaves the accumulator unchanged and moves to the next instruction. The value `x` is preserved in the instruction format but is **ignored** and not used in this question. 
- `"jump x"` leaves the accumulator unchanged, then moves to the instruction at the current index plus `x`.

**概要**:
- Simulate a simple bootloader program that may contain exactly one invalid branch instruction.
- Identify and flip at most one jump or next instruction to guarantee normal termination.
- Return the final accumulator value after applying the minimal necessary correction.

**考察点**:
- Graph reachability and cycle detection in execution traces
- State machine simulation with controlled modifications
- Reverse traversal to precompute termination paths
- Efficient validation of candidate corrections

**常用模式**:
- Graph Traversal
- DFS/BFS

**提示**:
- Model each instruction as a node in a directed graph where edges represent control flow; a non-terminating run indicates a cycle.
- Instead of testing every possible flip, simulate the original execution path and focus only on branch instructions encountered during that run.
- Precompute which nodes can reach the terminal state by traversing backward from the end, enabling O(1) validation of whether flipping a specific instruction fixes the loop.

**可能的 follow-up**:
- How would you adapt this approach if multiple instructions could potentially be flipped?
- Can the reverse graph be avoided by using only forward simulation and visited tracking?
- What is the time and space trade-off if we validate each potential flip independently?
- How would you handle cases where the program terminates immediately without any jumps?

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/hack2hire-premium.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/hack2hire-premium.md)。作者整理资料；许可和第三方来源范围见阅读指南。
