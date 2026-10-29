---
id: drustz-99a1cc9234fdc168fc
section: openai
order: 96
level: A
title: Implement Unix-like `cd` Command (with Symlink Follow-up)
quick: >-
  original-structured-preparation-guide · Implement Unix-like `cd` Command (with
  Symlink Follow-up)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/517354b3-4532-46e6-a31b-c8c2e999712e
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Unix-like `cd`：相对路径与 Symlink

## 基础题

给定当前目录 `cwd` 和目标路径，返回 `cd` 后的规范绝对路径。支持绝对/相对路径、`.`、`..` 和重复 `/`。

若目标是相对路径，先接到 cwd；按 `/` 拆分，用栈处理目录段：空段和 `.` 忽略，`..` 在非空时弹栈，普通名称入栈。根目录上的 `..` 仍停在根。

```python
def cd(cwd, target):
    source = target if target.startswith("/") else cwd.rstrip("/") + "/" + target
    stack = []
    for part in source.split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)
```



## Symlink 追问

解析到链接源时，把链接目标与尚未处理后缀重新加入待处理队列；相对链接目标以链接所在目录为基准。用访问状态 `(link, remaining_suffix)` 或展开次数上限检测环。

## 复杂度与边界

无链接时 `O(L)` 时间和空间；有链接时与实际展开后的总长度成正比。覆盖绝对目标忽略 cwd、链接在中间、链接目标含 `..`、多跳链接和 `/a -> /b -> /a`。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/517354b3-4532-46e6-a31b-c8c2e999712e)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
