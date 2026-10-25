---
id: stripe-shipping-cost
section: stripe
order: 1
level: S
title: Stripe：按国家、商品、数量算运费，三关递进
quick: >-
  三关共用一个函数：一关是单价乘数量，二关看数量落在哪个区间，用那个区间的单价乘整单数量，三关同一个区间可以改成一口价。2025 年 10 月实习生电面的算式是 5 台 laptop 全按 900，没有拆成两档相加。
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

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

按订单行的商品数量选择一个运费档位，计算该行运费。三阶段可复用同一接口：固定单价、按数量档位选择整行单价、档位支持固定总价。

### 输入与接口

实现 `line_cost`(qty,tiers)。qty为非负整数；tiers为有序规则列表，每项含min（非负整数闭下界）、max（整数闭上界或None表示无上界）、type（incremental或fixed）、cost（非负整数美分）。合法配置保证qty恰好命中一档，不要求测试缺失或冲突的配置。

### 输出与约束

返回该订单行的整数美分运费。选择满足min≤qty且max为空或qty≤max的档位；incremental返回qty×cost，fixed直接返回cost。不能把数量拆到多个档位逐段累加。

国家和商品的规则查找可由调用者用(country,product)键完成，line_cost只计算已经查到的规则。整单运费是各订单行费用之和。第一阶段可表示为一条min=0、max=None、type=incremental的规则；输入顺序不影响合法配置的唯一匹配结果。

### 示例

```text
laptop tiers=[{min:0,max:2,type:"incremental",cost:1000},{min:3,max:None,type:"incremental",cost:900}]
line_cost(2,tiers) -> 2000
line_cost(3,tiers) -> 2700
line_cost(5,tiers) -> 4500
line_cost(5,[{min:0,max:None,type:"fixed",cost:700}]) -> 700
20个mouse单价550、5台laptop按上述档位：总运费20×550+4500=15700美分
```

## 解题思路与参考答案

这题三关可以共用一个函数：按 `(country, product)` 取出区间表，看数量落在哪一档，`incremental` 就用这一档的单价乘全部数量，`fixed` 就直接取这一档的固定数。最容易错的是第二关，2025 年 10 月那场实习生电面的算式是 5 台 laptop 全按 900 算，没有拆成两档相加。

题来自 2025 年 10 月的 Stripe SDE Intern technical screen，HackerRank，大约一小时，就是一亩三分地反复提到的 shipping cost 题。三关，面试官测过才开下一关，过程里几乎不说话，最后五分钟反向提问。帖子说要自己造样例看输出。一亩三分地 2025 年 10 月也有人电面到同一道 shipping cost。数字以这篇实习生帖为准。

拿同一张订单走三关最清楚：美国订单，20 个 mouse、5 台 laptop。一关是固定单价，单价 550 和 1000，总价 `20*550 + 5*1000 = 16000`。二关 laptop 变成区间，0 到 2 台每台 1000，3 台及以上每台 900，mouse 仍是 550，同一张订单写成 `20*550 + 5*900 = 15700`。`maxQuantity` 可以是 null，表示没有上界。三关区间多一个 `type`：`incremental` 仍是数量乘这一档单价；`fixed` 是数量落进区间后，这一行运费就是那个固定数，不再乘数量。

第二关要按整单数量命中一档：5 台 laptop 全按 900 算。写成「2 台按 1000、3 台按 900」会得到另一种计费结果，和这帖的样例对不上。第三关则在命中区间后，再根据 type 决定乘数量还是取固定费用。键用 `(country, product)`，一关的表是单价，二关、三关的表是区间列表：

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

一关可以看成每条规则都是 `min=0, max=None, type=incremental`，这样三关共用一个函数，只换表。

边界帖子没写死。0 到 2 和 3+ 在数量 2、3 上是闭区间还是半开，要和面试官确认，样例没卡在边界上。缺国家或商品我会直接抛错，运费算少了就是少收钱。

还有一套流传的读法要知道。Prachub、DarkInterview 把二关写成按件跨档累加：前 2 台 1000，后面每台 900，5 台是 `2*1000 + 3*900`。三关的 fixed 也有人写成「走进这一档就加一次固定费」。这和上面的 15700 对不上。现场要是面试官说 each unit is priced by the tier it falls into，再改成跨档累加，别背完一套就不听题。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两档规则用数量 2 和 3 检查边界，数量 5 必须整行按 900 计为 4500。fixed 档收费与数量无关；缺少匹配区间应抛错。

```python
tiers = [{"min": 0, "max": 2, "type": "incremental", "cost": 1000},
         {"min": 3, "max": None, "type": "incremental", "cost": 900}]
assert line_cost(2, tiers) == 2000
assert line_cost(3, tiers) == 2700
assert line_cost(5, tiers) == 4500
assert line_cost(5, [{"min": 0, "max": None, "type": "fixed", "cost": 700}]) == 700
try:
    line_cost(1, [])
except ValueError:
    pass
else:
    raise AssertionError("missing tier must fail")
print("simple tests passed")
```

## 追问

**金额用 float 吗？**
不用。样例全是整数，我会用 int，单位是分。float 的精度误差可能让金额在分位上出现偏差。

**区间重叠或有洞怎么处理？**
建表时就拒绝。电面帖说不强制处理所有边界情况，我会在建表时按 `min` 排序，有重叠或有洞就拒绝这张配置，不在算钱时悄悄跳过。

**为什么二关最容易写错？**
人会把「匹配一档」写成「从 0 扫到 qty，每档加一段」。拿样例 15700 一对，马上就能看出写反了。
