---
id: drustz-0140ff027b7bcb7b81
section: forum-notes
order: 41
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 1: Basic File Management'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Part 1: Basic File Management'
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
## Part 1: Basic File Management

### Goal

The system needs to handle adding files, copying them, and checking their size.

### Commands

#### ADD_FILE

```text
ADD_FILE <name> <size>
```



- Creates a new file with the given `name`.
- `size` is the memory needed in bytes.
- **Fails** if a file with that name exists.
- Returns `"true"` if successful, otherwise `"false"`.

#### COPY_FILE

```text
COPY_FILE <nameFrom> <nameTo>
```



- Copies the file `nameFrom` to the new path `nameTo`.
- **Fails** if:

The source file does not exist.
- The source is a directory, not a file.
- A file already exists at the destination.
- Returns `"true"` if successful, otherwise `"false"`.

#### GET_FILE_SIZE

```text
GET_FILE\_SIZE <name>
```



- Returns the size of the file as a string.
- Returns an empty string `""` if the file is missing.

### Example Walkthrough

**Input:**

```javascript
[
  ["ADD_FILE", "/dir1/dir2/file.txt", "10"],
  ["COPY_FILE", "/root-existing_file.txt", "/dir1/file.txt"],
  ["COPY_FILE", "/dir1/dir2/file.txt", "/dir1/file.txt"],
  ["ADD_FILE", "/dir1/file.txt", "15"],
  ["COPY_FILE", "/dir1/file.txt", "/dir1/dir2/file.txt"],
  ["GET_FILE_SIZE", "/dir1/file.txt"],
  ["GET_FILE_SIZE", "/not-existing.file"],
];
```



**Result:** `["true", "false", "true", "false", "false", "10", ""]`

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
