---
id: drustz-9ec04fafc099a6cbd3
section: openai
order: 182
level: A
title: Resumable 2D Iterator with Pause and Resume Functionality
quick: >-
  original-structured-preparation-guide · Resumable 2D Iterator with Pause and
  Resume Functionality
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
      https://www.1point3acres.com/interview/problems/f37c572f-b9ee-482f-9eb5-420e03c340c2
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Resumable 2D Iterator：不规则矩阵的暂停与继续

## 证据边界

公开标题明确二维、pause/resume；同题族页面要求按行展开、跳过空行并处理不同长度。3D 或任意嵌套深度是后续版本，不在这里冒充当前 UUID 的唯一题面。

## 完整题面、接口与示例

输入 jagged list，按外层从左到右、每行从左到右返回元素，并提供可序列化状态：

```python
it = Resumable2DIterator([[], [1, 2], [], [3]])
next(it)  # 1
s = it.get_state()
next(it)  # 2
it.set_state(s)
next(it)  # 2
```



全为空时第一次 next 就停止；状态可停在某行最后一个元素之后，恢复后仍须正确跨过后续空行。

## 算法与关键状态

保存 `outer_index` 和 `inner_index`，二者始终表示下一个候选位置。next 用 while：若 outer 越界则停止；若 inner 已到当前行末尾，就 `outer+=1, inner=0` 并继续；否则返回当前元素并递增 inner。不要用递归跳空行，否则成千上万条空行可能爆栈。state 加 schema 与数据版本；set_state 校验字段、范围和版本后原子更新。可以保留“行尾未normalization”状态，只要 next 的规范化逻辑一致。

## 复杂度与边界

每个元素返回一次、每行跳过一次，完整遍历为 `O(R+E)`，R 是行数、E 是元素数；单次 next 摊还 `O(1)`，最坏可能连续跳 `O(R)` 个空行。额外游标空间 `O(1)`。测试空外层、首尾/连续空行、长度不一、行间保存、结束状态、非法 outer/inner、恢复到不同矩阵，以及迭代期间行被替换或缩短。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/f37c572f-b9ee-482f-9eb5-420e03c340c2)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
