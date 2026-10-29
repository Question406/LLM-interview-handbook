---
id: drustz-bf29ea32dcb7f9ba3d
section: openai
order: 129
level: A
title: 'GPU Credits II (Modified): Balance Query Returns None When Subtract Fails'
quick: >-
  original-structured-preparation-guide · GPU Credits II (Modified): Balance
  Query Returns None When Subtract Fails
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
      https://www.1point3acres.com/interview/problems/27d03a78-b011-4752-b7f4-b9aa6f92ad54
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# GPU Credits II：扣减失败后的 `None` 语义

> 这条修改版并不是“带有效期 grant 的额度账本”。旧正文映射错误，现按公开描述改为每用户余额状态机。

## 状态

```text
balance[user] = current balance
last_subtract_failed[user] = 最近一次 subtract 是否失败
```



- `add(user, amount)`：增加余额并清除失败标记；
- `subtract(user, amount)`：足额时原子扣减并清除标记；不足时余额完全不变，只将标记设为 true；
- `getBalance(user)`：标记为 true 时返回 `None`，否则返回余额；GET 本身不清标记。

```python
def subtract(user, amount):
    if amount < 0:
        raise ValueError("amount must be non-negative")
    if balance.get(user, 0) < amount:
        failed[user] = True
        return False
    balance[user] = balance.get(user, 0) - amount
    failed[user] = False
    return True
```



## 复杂度与边界

三种操作平均 `O(1)`，空间 `O(users)`；并发时同一用户需一把锁或数据库条件更新。覆盖未知用户余额 0、subtract 0、连续失败、失败后 add、失败后成功 subtract、大整数和禁止负 amount。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/27d03a78-b011-4752-b7f4-b9aa6f92ad54)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
