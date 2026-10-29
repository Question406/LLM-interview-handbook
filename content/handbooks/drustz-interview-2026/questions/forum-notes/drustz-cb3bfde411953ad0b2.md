---
id: drustz-cb3bfde411953ad0b2
section: forum-notes
order: 97
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 4: History and Rollbacks'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 4: History and Rollbacks'
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
## Level 4: History and Rollbacks

### Goal

Stop overwriting data. Instead, save every change as a new "version" of the recipe.

### Changes to Existing Functions

#### edit_recipe (Updated)

```text
edit_recipe(self, user_id: str, recipe_id: str, name: str, ingredients: list[str]) -> bool
```



- Now, this function **adds a new version** to the history list instead of deleting the old data.
- Versions are numbered (1, 2, 3...).
- The newest version is the "current" one.
- All validation rules from Level 3 still apply.

### New Functions

#### get_recipe_history

```text
get_recipe_history(self, recipe_id: str) -> list[dict] | None
```



- Returns a list of all versions for a recipe.
- The list is ordered from oldest to newest.
- Returns `None` if the recipe is missing.

#### rollback_recipe

```text
rollback_recipe(self, user_id: str, recipe_id: str, version: int) -> bool
```



- Copies an old version and saves it as the **newest** version.
- This does NOT delete any history. It just adds a copy of the old data to the end of the list.
- Returns `True` if successful.
- Returns `False` if:

The user or recipe is invalid.
- The version number does not exist.
- The old name now conflicts with another recipe's current name.
**Example:**

- History: v1("Pasta"), v2("Spaghetti").
- `rollback_recipe` to version 1.
- Result: v1("Pasta"), v2("Spaghetti"), v3("Pasta").

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
