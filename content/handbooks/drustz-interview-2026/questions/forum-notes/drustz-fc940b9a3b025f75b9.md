---
id: drustz-fc940b9a3b025f75b9
section: forum-notes
order: 337
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Complexity and Improvements'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Complexity and Improvements'
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
## Part 2: Complexity and Improvements

After coding the basic version, discuss these points:

### Time Complexity

- **Allocation**: **O(n)**. You might have to check every free block to find space.
- **Deallocation**: **O(n)**. You might have to search the list to find the right spot to insert or merge the freed block.

### Space Complexity

- **O(m)** where `m` is the number of free blocks.
- If memory is very chopped up (fragmented), this list can get long.

### Weaknesses

- **External Fragmentation**: Over time, you get many tiny empty gaps. You might have 100 bytes free total, but if they are in 10-byte chunks, you cannot allocate a 50-byte block.
- **Slow Search**: Scanning the list takes O(n) time.
- **No Moving**: You cannot move allocated data to close the gaps.

### How to Optimize

**To Fix Fragmentation:**

- **Segregated Free Lists**: Keep different lists for different sizes (e.g., one list for small blocks, one for large). This is faster and cleaner.
- **Best-Fit Strategy**: Don't just take the *first* block. Find the *smallest* block that fits. This saves large blocks for later but takes longer to search.
- **Buddy System**: Divide memory into powers of 2 (e.g., 2, 4, 8, 16). This makes merging very fast and easy.
**To Improve Speed:**

- **Balanced Binary Search Tree (BST)**: Organize free blocks in a tree. This makes searching and adding blocks take **O(log n)** time instead of O(n).
- **Bitmap**: If all blocks are the same size, use a bitmap. This allows **O(1)** allocation.
**To Improve Space:**

- **Implicit Free List**: Don't use a separate Python list. Write the block size and status directly inside the memory itself (in a header).
- **Boundary Tags**: Add a footer to every block. This lets you look backward in memory instantly (**O(1)**) to merge with the previous block.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
