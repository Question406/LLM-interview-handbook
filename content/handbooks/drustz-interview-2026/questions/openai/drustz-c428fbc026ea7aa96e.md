---
id: drustz-c428fbc026ea7aa96e
section: openai
order: 179
level: A
title: Maximize Rice Units Taken Without Emptying Piles Using DP
quick: >-
  original-structured-preparation-guide · Maximize Rice Units Taken Without
  Emptying Piles Using DP
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
      https://www.1point3acres.com/interview/problems/3b674fd2-33ac-43c2-964d-526dffa9dc9a
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Rice Piles：公开题面存在矛盾

> 这条题目的公开描述和公开样例不能同时成立。与其编造一个 DP，不如先把矛盾指出来，并说明需要补充什么条件。

## 公开描述的字面含义

公开页面大意是：可以从任意米堆开始，之后移动到相邻米堆；从每堆拿走任意数量，但不能把任何一堆拿空；目标是拿到最多的米。

公开样例是：

```text
piles = [3, 4, 5, 1, 2]
公开输出 = 9
```



## 为什么矛盾

如果字面规则允许依次访问所有相邻米堆，那么可以从每一堆取走 `pile - 1`：

```text
2 + 3 + 4 + 0 + 1 = 10
```



这已经大于公开输出 9。并且字面版本根本不需要 DP，只需：

```python
def literal_answer(piles: list[int]) -> int:
    return sum(max(0, pile - 1) for pile in piles)
```



时间为 `O(n)`，额外空间为 `O(1)`。

## 面试时应该先确认

缺失条件可能是：

- 有总步数或移动次数限制；
- 每个米堆只能访问一次；
- 只能选择某种受限路径；
- 每次拿取数量受前后米堆影响；
- 起点、终点或方向受到限制。

在这些条件补齐之前，不存在可验证的“标准 DP 解”。本地页面因此只保留矛盾分析，不把猜测包装成原题答案。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/3b674fd2-33ac-43c2-964d-526dffa9dc9a)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
