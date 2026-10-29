---
id: afm-rm-bias-audit-code
section: alignment
order: 131
level: S
title: 编程：交换 AB／BA 后还原身份，计算 position bias 审计表
quick: 先把 first/second 映射回 A/B 身份，再分稳定胜负、tie 与不一致。交换平均分与顺序一致率是不同指标，不能把顺序不一致伪装成内容 tie。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 完整编程练习
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-27'
sources:
  - title: Large Language Models are not Fair Evaluators
    url: 'https://arxiv.org/abs/2305.17926'
    type: primary
---

## 题目描述

同一对回答被 LLM judge 评价两次：第一次展示 A 在前、B 在后；第二次交换顺序，展示 B 在前、A 在后。Judge 只返回更喜欢第一个、第二个，或者 tie。请还原候选身份，并汇总顺序交换后的稳定性与 first-position preference。

这是 position-bias 的描述性审计，不要求训练 reward model，也不能只凭这些结果证明 causal bias 或回答的真实质量。接口为原创练习约定。

### 接口与输入

实现 `audit_positions(rows)`。`rows` 是非空的 Python `list[dict]`。每条记录含 `ab`、`ba` 两个字符串字段，值保证是 `"first"`、`"second"`、`"tie"` 之一；不得修改 rows 或内部字典。

| 字段 | 展示顺序 | first 对应 | second 对应 |
| --- | --- | --- | --- |
| `ab` | A, B | A | B |
| `ba` | B, A | B | A |

一行的两次评价来自同一内容对，但不同记录可以对应不同 prompts。`tie` 表示 judge 本次不给出 winner，不等于顺序交换后结果不一致。

### 输出字段与精确定义

返回含以下 7 个字段的字典：

- `n`：输入记录数，Python int。
- `stable_a`：两次评价还原后都选择 A 的记录数。
- `stable_b`：两次评价还原后都选择 B 的记录数。
- `stable_tie`：两次都为 tie 的记录数。
- `inconsistent`：其余记录数，包括一次 tie、另一次选择具体候选。
- `swap_score`：将全部 `2*n` 次评价映射为 A 的分数后取均值。选 A 为 1，选 B 为 0，tie 为 0.5；返回 Python float。
- `first_rate`：在全部非 tie 的展示中，选择 first 的次数除以非 tie 展示次数。分母为 0 时返回 `None`，否则返回 Python float。

四类记录计数之和必须等于 n。`swap_score` 的分母始终是 `2*n`；`first_rate` 的分母排除 tie，不能混用两种分母。目标时间复杂度为 O(n)，额外空间 O(1)，不计返回字典。

### 完整输入输出示例

```text
rows=[
  {"ab":"first", "ba":"second"},
  {"ab":"first", "ba":"first"},
  {"ab":"tie",   "ba":"tie"}
]
audit_positions(rows) -> {
  "n":3,
  "stable_a":1,
  "stable_b":0,
  "stable_tie":1,
  "inconsistent":1,
  "swap_score":0.6666666666666666,
  "first_rate":0.75
}
```

第一行两次都选 A；第二行分别选 A、B；第三行两次 tie。A 总得分为 `2+1+1=4`，除以 6；非 tie 展示有 4 次，其中 3 次选 first。

```text
rows=[{"ab":"tie","ba":"tie"}]
返回 {"n":1,"stable_a":0,"stable_b":0,"stable_tie":1,
      "inconsistent":0,"swap_score":0.5,"first_rate":None}
```

## 解题思路与参考答案

核心是身份映射；AB 与 BA 的 first 表示不同候选。此表应搭配独立真标签才能评质量，不可由 first_rate 直接推断内容无偏。时间 O(n)，额外空间 O(1)。

```python
def audit_positions(rows):
    result = dict(n=len(rows), stable_a=0, stable_b=0, stable_tie=0, inconsistent=0)
    total = first = non_tie = 0
    for row in rows:
        a = {"first": "A", "second": "B", "tie": "tie"}[row["ab"]]
        b = {"first": "B", "second": "A", "tie": "tie"}[row["ba"]]
        key = (
            {"A": "stable_a", "B": "stable_b", "tie": "stable_tie"}[a]
            if a == b
            else "inconsistent"
        )
        result[key] += 1
        total += {"A": 1, "B": 0, "tie": 0.5}[a] + {"A": 1, "B": 0, "tie": 0.5}[b]
        for value in (row["ab"], row["ba"]):
            non_tie += value != "tie"
            first += value == "first"
    result["swap_score"] = total / (2 * len(rows))
    result["first_rate"] = first / non_tie if non_tie else None
    return result
```

## 简单测试怎么写

将实现和下面测试放入 solution.py，用普通 Python 运行，无需 PyTorch。先核对完整三行示例，再检查全 tie、一次 tie、顺序反转与输入保持；这里没有训练、gradient 或 validation split。

```python
import copy

full = audit_positions(
    [
        dict(ab="first", ba="second"),
        dict(ab="first", ba="first"),
        dict(ab="tie", ba="tie"),
    ]
)
assert full == dict(
    n=3,
    stable_a=1,
    stable_b=0,
    stable_tie=1,
    inconsistent=1,
    swap_score=2 / 3,
    first_rate=0.75,
)
rows = [dict(ab="first", ba="first")]
saved = copy.deepcopy(rows)
r = audit_positions(rows)
assert r["inconsistent"] == 1 and r["swap_score"] == 0.5 and r["first_rate"] == 1
assert rows == saved
r = audit_positions(
    [
        dict(ab="first", ba="second"),
        dict(ab="second", ba="first"),
        dict(ab="tie", ba="tie"),
    ]
)
assert (r["stable_a"], r["stable_b"], r["stable_tie"], r["inconsistent"]) == (
    1,
    1,
    1,
    0,
)
assert r["swap_score"] == 0.5 and r["first_rate"] == 0.5
r = audit_positions([dict(ab="tie", ba="tie")])
assert r["first_rate"] is None and r["stable_tie"] == 1
r = audit_positions([dict(ab="tie", ba="first")])
assert r["inconsistent"] == 1 and r["swap_score"] == 0.25
```

## 面试追问

说明如何在不保存全部记录的条件下累计这些计数，以及如何按 judge version、task type 分组分析。First rate 接近 0.5 仍不证明内容质量无偏；下一步需要独立 labels 或受控对照。
