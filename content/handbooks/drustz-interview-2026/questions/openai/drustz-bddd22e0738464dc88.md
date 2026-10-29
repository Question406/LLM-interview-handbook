---
id: drustz-bddd22e0738464dc88
section: openai
order: 137
level: A
title: General Coding Interview
quick: original-structured-preparation-guide · General Coding Interview
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
      https://www.1point3acres.com/interview/problems/ced5e63d-df6c-4a76-8166-add49305f598
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# General Coding：无重复整数数组求和

## 题目要做什么

给定一个没有重复元素的整数数组，返回所有元素的总和。

这是一道基础题。既然题目已经保证元素不重复，就不需要额外构建 set；创建 set 反而会增加不必要的空间。

```python
def array_sum(values: list[int]) -> int:
    total = 0
    for value in values:
        total += value
    return total
```



## 正确性

循环处理完前 `i` 个元素后，`total` 恰好等于这 `i` 个元素之和。初始时处理 0 个元素，总和为 0；每一步加入下一个元素后不变量继续成立，所以最终得到全部元素之和。

## 复杂度

时间为 `O(n)`，辅助空间为 `O(1)`。

## 边界

空数组通常返回 0，但应核对原题约定；还要考虑负数、单元素，以及 Java/C++ 等固定宽度整数类型是否可能溢出。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ced5e63d-df6c-4a76-8166-add49305f598)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
