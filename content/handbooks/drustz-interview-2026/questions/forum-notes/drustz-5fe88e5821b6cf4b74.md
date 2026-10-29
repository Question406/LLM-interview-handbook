---
id: drustz-5fe88e5821b6cf4b74
section: forum-notes
order: 335
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Core Requirements
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Core Requirements
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
## Core Requirements

You must write a `MemoryAllocator` class with these specific features:

### Initialization

```text
def __init__(self, total_capacity: int)
```



- **total_capacity**: The total size of the memory in bytes.
- The system starts with all memory marked as "free" (empty).

### Methods

#### 1. `allocate(size: int) -> int`

This asks for a block of memory.

- **Input**: `size` (How much memory you need).
- **Output**: The starting index (address) of the new block.
- **How it works**:

Look for the first empty spot that is big enough (First-fit strategy).
- Mark that spot as "taken".
- Return the starting address.
- **Errors**:

Raise an error if `size` is zero or negative.
- Raise an error if there isn't enough contiguous memory.

#### 2. `free(address: int, size: int) -> None`

This returns memory back to the system.

- **Input**:

`address`: The starting index of the block.
- `size`: How big the block is.
- **How it works**:

Mark this section of memory as "free".
- Check if the memory right next to it is also free. If yes, join them together to make one big empty spot.
- **Errors**:

Raise an error if the address is outside the memory limits.
- Raise an error if you try to free memory that wasn't allocated.
- Raise an error if the size is wrong.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
