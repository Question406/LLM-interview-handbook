---
id: drustz-d867f3eaf2a8fe513c
section: forum-notes
order: 118
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Faster Solution
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Faster Solution
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
## Faster Solution

Hashing the entire content of every file is slow if the files are large. We can use a **multi-step process** to avoid reading full files when we don't have to.

### Three-Step Process

- **Step 1 - Check File Size:**

Group files by their size first.
- If two files have different sizes, they cannot be duplicates.
- This is very fast because we only read metadata, not the file content.
- **Step 2 - Check Partial Hash:**

For files that have the same size, read only the first small part (like 1024 bytes).
- Hash this small part.
- If the beginning of the files is different, they are not duplicates.
- **Step 3 - Check Full Hash:**

Only calculate the full hash if the size **and** the partial hash match.
- This ensures the answer is correct but saves a lot of time.

### How Fast is It?

- **Best case:** Most files have unique sizes. We only check metadata. Complexity: O(number of files).
- **Worst case:** All files are the same size and start with the same data. We must hash everything. Complexity: O(total file size).
- **Average case:** Much faster than the simple solution because we filter out most non-duplicates early.

### Code Structure

```python
def find_duplicate_files_optimized(root_path: str) -> List[List[str]]:
    # Step 1: Group by file size
    size_groups = group_by_file_size(root_path)
    # Result: {size1: [file1, file2, ...], size2: [file3, ...], ...}

    # Step 2: For each size group, compute partial hash
    partial_hash_groups = {}
    for files in size_groups.values():
        if len(files) > 1:
            group_by_partial_hash(files, partial_hash_groups)
    # Result: {partial_hash1: [file1, file2, ...], partial_hash2: [file3, ...], ...}
    # Note: Step 3 will handle rare collisions across different sizes

    # Step 3: For each partial hash group, compute full hash
    full_hash_groups = {}
    for files in partial_hash_groups.values():
        if len(files) > 1:
            group_by_full_hash(files, full_hash_groups)
    # Result: {full_hash1: [file1, file2, ...], full_hash2: [file3, ...], ...}

    # Return only groups with duplicates
    return [files for files in full_hash_groups.values() if len(files) > 1]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
