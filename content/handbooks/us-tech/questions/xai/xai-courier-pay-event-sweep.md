---
id: xai-courier-pay-event-sweep
section: xai
order: 936
level: A
title: "xAI：从 ACCEPT / FULFILL events 计算 courier pay"
quick: "我会先确认付费单位：这里每单都计费，所以两单同时 active 十分钟，要算二十个 order-minutes。金额用 integer cents，避免浮点误差。"
companies:
  - xai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：xAI：从 ACCEPT / FULFILL events 计算 courier pay"
    url: "https://landthelab.com/questions/courier-pay-from-order-events"
    type: secondary
---

## 题目描述

来源：Land the Lab 的 xAI 目录收录 courier pay。下面使用公开页的每个 active order 每分钟 30 cents 规则，并将非法 event sequence 的处理补成明确接口。

### 输入、接口与规则

实现 `courier_pay(events, rate_cents=30) -> int`。输入 events 为 `(minute, order_id, kind)` list，minute 为非负整数，kind 为 ACCEPT 或 FULFILL。输入可以无序，每个 order 必须恰有一个 ACCEPT 与一个 FULFILL，且 ACCEPT minute≤FULFILL minute。Order ID 为可排序 string，rate_cents 为非负整数。

一个 order 在 `[accept,fulfill)` 时间内 active；每分钟为每个 active order 累加 rate_cents，重叠 orders 分别计费。返回整数 cents。空 events 返回 0；重复 ACCEPT、缺失 partner、FULFILL 早于 ACCEPT、未知 kind 均抛 ValueError。同一 minute 不产生额外时长，且 ACCEPT 排在 FULFILL 前处理；不修改 events。

### 输入输出示例

```text
events=[(0,"a","ACCEPT"),(10,"b","ACCEPT"),(20,"a","FULFILL"),(30,"b","FULFILL")]
两单各 active 20 分钟，rate_cents=30 -> 返回 1200 cents。
同一单在 minute=5 ACCEPT 与 FULFILL -> 0。
```

## 回答思路

> **Situation / Task：** 按每个 active order 计费，重叠时间不能只算一次。  
> **Approach / Why：** 先验证每单 timestamps，再 sweep 排序后的 events，用 active_count 积分。  
> **Result / Check：** 用每单 duration 求和作为独立 oracle，检查乱序与同刻 events。

## 解题思路与参考答案

我会先确认付费单位：这里每单都计费，所以两单同时 active 十分钟，要算二十个 order-minutes。金额用 integer cents，避免浮点误差。

排序后，每到一个 event，先用“当前 minute 减上一 minute”乘旧 active count 累加，再更新 active count。同一时刻 events 的间隔为零，因此不会多收费。验证逻辑独立检查每个 order 的完整性，不能只看最终 active count 是否归零。

### 完整参考实现

```python
def courier_pay(events, rate_cents=30):
    if rate_cents < 0:
        raise ValueError('negative rate')
    orders = {}
    for minute, order, kind in events:
        if minute < 0 or kind not in ('ACCEPT', 'FULFILL'):
            raise ValueError('invalid event')
        times = orders.setdefault(order, {})
        if kind in times:
            raise ValueError('duplicate event')
        times[kind] = minute
    for times in orders.values():
        if set(times) != {'ACCEPT', 'FULFILL'} or times['ACCEPT'] > times['FULFILL']:
            raise ValueError('unpaired or reversed event')
    ordered = sorted(events, key=lambda e: (e[0], e[2] != 'ACCEPT', e[1]))
    last = 0
    active = 0
    total = 0
    for minute, order, kind in ordered:
        total += (minute - last) * active * rate_cents
        active += 1 if kind == 'ACCEPT' else -1
        last = minute
    return total
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
events = [
    (0, 'a', 'ACCEPT'),
    (10, 'b', 'ACCEPT'),
    (20, 'a', 'FULFILL'),
    (30, 'b', 'FULFILL'),
]
assert courier_pay(events) == 1200
assert courier_pay([(5, 'a', 'FULFILL'), (5, 'a', 'ACCEPT')]) == 0
assert courier_pay([]) == 0
from random import Random

rng = Random(14)
for _ in range(100):
    events = []
    expected = 0
    for i in range(20):
        a = rng.randrange(50)
        b = a + rng.randrange(20)
        events.extend([(a, str(i), 'ACCEPT'), (b, str(i), 'FULFILL')])
        expected += (b - a) * 30
    rng.shuffle(events)
    assert courier_pay(events) == expected
for invalid in [
    [(0, 'a', 'ACCEPT')],
    [(0, 'a', 'ACCEPT')] * 2,
    [(1, 'a', 'ACCEPT'), (0, 'a', 'FULFILL')],
]:
    try:
        courier_pay(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid events accepted')
print('courier pay tests passed')
```

## 复杂度与追问

Events 数 E，排序时间 `O(E*log E)`，额外空间 `O(E)`。题设按单线性计费时也可直接累加每单 duration；sweep 便于扩展 active-count-dependent rates，但新定价规则要重新定义。
