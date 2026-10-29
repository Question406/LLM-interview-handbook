---
id: drustz-b0636d90e4cb0b6a11
section: anthropic
order: 94
level: A
title: File Profiler
quick: original-structured-preparation-guide · File Profiler
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
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
      https://www.1point3acres.com/interview/problems/dc568545-f217-4ade-8ba3-30d633579af6
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# File Profiler（文件统计器）

## 题目要做什么

给定一个文件和一个目标词，输出：

1. 文件总行数；
2. 单词总数；
3. 目标词出现次数；
4. 文件大小，单位为字节。

## 流式解法

逐行读取文件。每读一行，就累加行数，并用空白切分单词，更新总单词数和目标词计数。字节大小应从文件元数据读取，不能用decoding后的字符串长度代替。

```python
import os


def profile_file(path: str, target: str) -> dict[str, int]:
    result = {"lines": 0, "words": 0, "occurrences": 0, "bytes": 0}

    with open(path, "r", encoding="utf-8", newline=None) as file:
        result["bytes"] = os.fstat(file.fileno()).st_size

        for line in file:
            result["lines"] += 1
            for word in line.split():
                result["words"] += 1
                if word == target:
                    result["occurrences"] += 1

    return result
```



## 复杂度

设文件大小为 `B`、最长一行长度为 `L`。时间为 `O(B)`，逐行方案的额外空间为 `O(L)`。如果允许单行无限长，可改为固定大小分块读取。

## 必须说明的口径

上面的实现采用“按空白切词、区分大小写、标点属于单词”的定义。因此 `word,` 不等于 `word`。如果要求忽略标点或大小写，需要先做统一规范化。

## 边界

空文件、没有末尾换行的单行文件、文件不存在、权限不足、路径是目录、非法 UTF-8，以及统计期间文件被其他进程修改。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/dc568545-f217-4ade-8ba3-30d633579af6)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
