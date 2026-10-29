---
id: drustz-6c026ffd3cda245cdd
section: forum-notes
order: 96
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 3: Adding Users'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 3: Adding Users'
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
## Level 3: Adding Users

### Goal

Add a user system. Some actions now require a valid user ID to work.

### New Functions

#### add_user

```text
add_user(self, user_id: str, username: str) -> bool
```



- Creates a new user.
- Returns `True` if created.
- Returns `False` if the user ID already exists.

#### edit_recipe

```text
edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool
```



- Updates a recipe, but checks the user first.
- Returns `True` if successful.
- Returns `False` if:

The `user_id` is invalid.
- The `recipe_id` does not exist.
- The new name is taken by another recipe.
**Note:** This function replaces the old update logic. It does the same thing but adds a user check.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
