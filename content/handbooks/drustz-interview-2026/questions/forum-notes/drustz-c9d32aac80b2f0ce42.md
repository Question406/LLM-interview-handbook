---
id: drustz-c9d32aac80b2f0ce42
section: forum-notes
order: 44
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 4: Compressing Files'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 4: Compressing Files'
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
## Part 4: Compressing Files

### Goal

Add the ability to compress files to save space.

### New Commands

#### COMPRESS_FILE

```text
COMPRESS_FILE <userId> <name>
```



- Compresses a file if it belongs to `userId`.
- **Action**:

Rename the file to `<name>.COMPRESSED`.
- Change the file size to exactly **half** of the original.
- **Fails** if the file is already compressed (names ending in `.COMPRESSED` cannot be compressed again).
- Returns the **remaining storage space** for the user.
- Returns `""` if the operation fails.
**Note**: `COPY_FILE` preserves the `.COMPRESSED` suffix.

#### DECOMPRESS_FILE

```text
DECOMPRESS_FILE <userId> <name>
```



- Unzips a file if it belongs to `userId`.
- **Action**: Revert the name by removing `.COMPRESSED`.
- **Fails** if:

The unzipped file makes the user go over their storage limit.
- A file with the original name already exists.
- Returns the **remaining storage space** for the user.
- Returns `""` if the operation fails.

### Example Walkthrough

**Input:**

```javascript
[
  ["ADD_USER", "user1", "1000"],
  ["ADD_USER", "user2", "5000"],
  ["ADD_FILE_BY", "user1", "/dir/file.mp4", "500"],
  ["COMPRESS_FILE", "user2", "/dir/file.mp4"],
  ["COMPRESS_FILE", "user3", "/dir/file.mp4"],
  ["COMPRESS_FILE", "user1", "/folder/non_existing_file"],
  ["COMPRESS_FILE", "user1", "/dir/file.mp4"],
  ["GET_FILE_SIZE", "/dir/file.mp4.COMPRESSED"],
  ["GET_FILE_SIZE", "/dir/file.mp4"],
  ["COPY_FILE", "/dir/file.mp4.COMPRESSED", "/file.mp4.COMPRESSED"],
  ["ADD_FILE_BY", "user1", "/dir/file.mp4", "500"],
  ["DECOMPRESS_FILE", "user1", "/dir/file.mp4.COMPRESSED"],
  ["UPDATE_CAPACITY", "user1", "2000"],
  ["DECOMPRESS_FILE", "user2", "/dir/file.mp4.COMPRESSED"],
  ["DECOMPRESS_FILE", "user3", "/dir/file.mp4.COMPRESSED"],
  ["DECOMPRESS_FILE", "user1", "/dir/file.mp4.COMPRESSED"],
  ["DECOMPRESS_FILE", "user1", "/file.mp4.COMPRESSED"],
];
```



**Result:** `["true", "true", "500", "", "", "", "750", "250", "", "true", "0", "", "0", "", "", "", "750"]`

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100005*)

---

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
