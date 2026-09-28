---
id: rippling-driver-pay
section: rippling
order: 1
level: S
title: Rippling：外卖员时薪结算，pay_up_to 不能双付
quick: >-
  addDriver、recordDelivery、getTotalCost，再加 pay_up_to 和未付金额。单子只在结束后写入。
  pay_up_to 只结算 end 不超过截止时间的整单，同一单不能付两次。
tags:
  - Rippling
  - Coding
  - Intervals
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Rippling 店面过经，Driver Cost，2025-04
    url: https://www.1point3acres.com/bbs/thread-1121843-1-1.html
    type: candidate-first-hand
  - title: Rippling SDE-2 Phone Screening，payUpToTime
    url: https://leakcode.dev/question/33096
    type: secondary
  - title: Delivery Billing System
    url: https://www.1point3acres.com/interview/problems/2a5d3aec-fd17-4ff7-9211-97a10e2a67b7
    type: secondary
  - title: Rippling SDE-1 Interview Experience (2026)
    url: https://medium.com/@parul947a/rippling-sde-1-interview-experience-2026-7583fe7ff8aa
    type: candidate-first-hand
---

## 真题记录

2025 年 4 月 Rippling 店面，作者原文是给外卖员算薪水。

- `add_driver(driver_id, usd_hourly_rate)`
- `record_delivery(driver_id, start_time, end_time)`：订单完成后才写入
- `get_total_cost()`：平台要付的总工资

后面加 `pay_up_to(pay_time)`。楼主回复：只付已经结束的单。因为 record 只在结束时写入，所以不存在「start 在截止前、end 在截止后、人还在送」这种输入。重复支付不能发生。有现成测试，明显的边界建议自己提出来并用 print 看。

2026 年 2 月另一则 SDE-2 电面（LeakCode 转的 Reddit）API 名字略不同：`addDriver`、`addDelivery(start, end)`、`getTotalCost`，然后 `payUpToTime` 和 `getCostToBePaid`。作者把未付写成总额减去已付，面试官说线性扫区间可以。这轮测试过了，人还是被拒了。

一亩三分地后来的题库页把约束写得更满：Unix 秒、一单最长约 3 小时、工资等于时薪乘秒数再除以 3600、重叠时段各算各的、只标记结束时间不超过截止时间的整单。电话面那帖没写 3 小时和重叠，现场以面试官的测试为准。

2025 年 8 月投、11 月面的 SDE-1 是另一条流程：60 分钟 OA 两题，其中一题用到并查集；onsite 两道图，第二道是第一道的 follow-up；然后一道 document analyzer 的面向对象实现；最后 hiring manager 挖一个项目。那篇没有给出函数表。来源是 Medium 上的个人复盘，不单列成题。

## 我会怎么写

总工资在记单一笔时加上，查询是 O(1)。付款只把还没付、且结束时间不超过截止时间的单标成已付。

```python
class Payroll:
    def __init__(self):
        self.rate = {}
        self.rows = []  # end, cost_cents, paid
        self.total = 0

    def add_driver(self, driver_id, usd_hourly_rate):
        self.rate[driver_id] = usd_hourly_rate

    def record_delivery(self, driver_id, start, end):
        cents = round(self.rate[driver_id] * (end - start) / 3600 * 100)
        self.rows.append([end, cents, False])
        self.total += cents

    def get_total_cost(self):
        return self.total

    def pay_up_to(self, pay_time):
        for row in self.rows:
            if not row[2] and row[0] <= pay_time:
                row[2] = True

    def unpaid(self):
        return sum(cents for end, cents, paid in self.rows if not paid)
```

面试若用 double 才能对上他们的测试，先按 double 写，口头说明生产里用整数分。`round` 的方向（银行家舍入还是向上）要问，钱上的默认舍入不算对。

## 错法

把跨过截止时间的单按秒切开。这帖的数据里没有这种单。写了切片，会和「只付已结束的整单」的测试不一致。

每次付款都把所有已结束的单再加进已付金额，却没有已付标记。同一截止时间调用两次，工资翻倍。

## 追问

**两单时间重叠？** 题库页写重叠也各付各的，时薪按单计，不按人把时间并起来。电话面没说的话，先问再写。

**截止时间比上次更早？** 已付的单保持已付。更早的截止时间不能把钱退回去。

**单子在付款之后才补录？** 补录的单初始未付。结束时间若已经早于上次截止时间，下一次用同一个或更晚的时间会把它付掉。不要在补录时自动当成已付，除非面试官这么说。
