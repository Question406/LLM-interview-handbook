---
id: drustz-02ea6a8b55f0dff166
section: anthropic
order: 42
level: A
title: Find All Possible Recipes from Given Supplies
quick: >-
  original-structured-preparation-guide · Find All Possible Recipes from Given
  Supplies
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
      https://www.1point3acres.com/interview/problems/89c84243-c0ab-5947-8e9b-9a29a3f7895c
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Find All Possible Recipes from Given Supplies

## 题目要做什么

给定 recipes、每个 recipe 所需的 ingredients，以及初始 supplies。做出来的 recipe 也可以作为其他 recipe 的 ingredient。返回所有最终能够制作的 recipes。

## 拓扑排序

把“ingredient → recipe”建成有向边。`missing[recipe]` 表示还有多少种原料没获得。初始 supplies 入队；每取出一种可用物品，就把所有依赖它的 recipe 的 missing 减一，减到 0 的 recipe 变成新的 supply 并入队。

```python
from collections import defaultdict, deque


def find_all_recipes(recipes, ingredients, supplies):
    dependents = defaultdict(list)
    missing = {}

    for recipe, needs in zip(recipes, ingredients):
        missing[recipe] = len(needs)
        for item in needs:
            dependents[item].append(recipe)

    queue = deque(supplies)
    answer = []
    while queue:
        item = queue.popleft()
        for recipe in dependents[item]:
            missing[recipe] -= 1
            if missing[recipe] == 0:
                answer.append(recipe)
                queue.append(recipe)
    return answer
```



## 复杂度与边界

设 ingredient 引用总数为 `E`，时间和空间都是 `O(E + recipes + supplies)`。需要考虑依赖环、未知原料、recipe 名与 supply 重名，以及同一 ingredients 列表是否可能重复同一种原料。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/89c84243-c0ab-5947-8e9b-9a29a3f7895c)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
