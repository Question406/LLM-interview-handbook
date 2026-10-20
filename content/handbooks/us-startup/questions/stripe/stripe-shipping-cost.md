---
id: stripe-shipping-cost
section: stripe
order: 1
level: S
title: Stripe：按国家、商品、数量算运费，三关递进
quick: >-
  一关是单价乘数量。二关按数量落在哪个区间，用那个区间的单价乘整单数量。三关同一个区间可以改成一口价。
  2025 年 10 月实习生电面的算式是 5 台 laptop 全按 900，不是拆成两档相加。
tags:
  - Stripe
  - Coding
  - Parsing
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Stripe SDE Intern 面经，Technical Screen，2025-10-20
    url: https://learncswithus.com/2025/10/20/stripe-intern-screen/
    type: candidate-first-hand
  - title: 一亩三分地 Stripe 标签页（shipping cost 被多次点名）
    url: https://www.1point3acres.com/bbs/tag/stripe-2126-7.html
    type: secondary
  - title: Compute shipping cost with tiered pricing
    url: https://prachub.com/coding-questions/compute-shipping-cost-with-tiered-pricing-2
    type: secondary
---

## 真题记录

2025 年 10 月，Stripe SDE Intern technical screen，HackerRank，大约一小时。题是一亩三分地反复提到的 shipping cost 题。三关，面试官测过才开下一关。过程里几乎不说话，最后五分钟反向提问。帖子写要自己造样例看输出。一亩三分地 2025 年 10 月也有人电面同一道 shipping cost。

数字以这篇实习生帖为准。

一关，固定单价。美国订单 20 个 mouse、5 台 laptop，单价 550 和 1000，总价 `20*550 + 5*1000 = 16000`。

二关，区间。laptop：0 到 2 台每台 1000，3 台及以上每台 900。mouse 仍是 550。同一张订单写成 `20*550 + 5*900 = 15700`。`maxQuantity` 可以是 null，表示没有上界。

三关，区间多一个 `type`。`incremental` 仍是数量乘这一档单价。`fixed` 是数量落进区间后，这一行运费就是那个固定数，不再乘数量。

## 我会怎么写

键用 `(country, product)`。一关的表是单价。二关、三关的表是区间列表。

这篇帖的二关不是出租车计价。5 台没有拆成「2 台按 1000、3 台按 900」。数量整个落在某一档，就用那一档的单价乘全部数量。三关只是命中之后看 type。

```python
def line_cost(qty, tiers):
    hit = None
    for tier in tiers:
        hi = tier["max"]
        if qty >= tier["min"] and (hi is None or qty <= hi):
            hit = tier
            break
    if hit is None:
        raise ValueError("no tier")
    if hit["type"] == "fixed":
        return hit["cost"]
    return qty * hit["cost"]
```

一关可以看成每条规则都是 `min=0, max=None, type=incremental`。这样三关共用一个函数，只换表。

边界帖子没写死。0 到 2 和 3+ 在数量 2、3 上要和面试官确认是闭区间还是半开。样例没卡在边界上。缺国家或商品我会直接抛错：运费算少了就是少收钱。

## 另一套流传的读法

Prachub、DarkInterview 把二关写成按件跨档累加：前 2 台 1000，后面每台 900，5 台是 `2*1000 + 3*900`。三关的 fixed 也有人写成「走进这一档就加一次固定费」。这和上面的 15700 对不上。现场若面试官说 each unit is priced by the tier it falls into，再改成跨档累加。不要背完一套就不听题。

## 追问

**金额用 float 吗？** 样例全是整数。我会用 int，单位是分。float 的精度误差可能让金额在分位上出现偏差。

**区间重叠或有洞怎么处理？** 电面帖说不强制处理所有边界情况。我会在建表时按 `min` 排序，重叠或洞就拒绝这张配置，不在算钱时沉默跳过。

**为什么二关最容易写错？** 人会把「匹配一档」写成「从 0 扫到 qty，每档加一段」。样例 15700 能马上看出来写反了。
