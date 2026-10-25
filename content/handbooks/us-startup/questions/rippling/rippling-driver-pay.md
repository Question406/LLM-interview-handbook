---
id: rippling-driver-pay
section: rippling
order: 1
level: S
title: Rippling：外卖员时薪结算，pay_up_to 不能双付
quick: >-
  每单带一个已付标记，pay_up_to 只结算 end 不超过截止时间的整单，同一单就不会付两次。接口是 addDriver、recordDelivery、getTotalCost，再加 pay_up_to 和未付金额，总工资在记单时累加。单子只在结束后写入，所以不用处理跨截止时间的单。
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

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

实现外卖员工资台账：登记时薪、记录已完成配送、查询累计工资，并将截止时间前已完成的整单标记为已支付，避免重复支付。

### 输入与接口

实现 Payroll()，提供 `add_driver`(`driver_id`,`usd_hourly_rate`)、`record_delivery`(`driver_id`,start,end)、`get_total_cost`()、`pay_up_to`(`pay_time`)、unpaid()。driver_id为字符串；先登记再记单；时薪为非负有限美元数；start、end、pay_time使用Unix秒整数，start<end。每次record_delivery代表一笔不同的已完成订单。

### 输出与约束

每单金额单位为整数美分，按 round(`usd_hourly_rate`×(end-start)/3600×100) 计算，本练习沿用Python round的平票取偶约定。记单时固定金额；之后更新同司机时薪只影响新订单。同一司机重叠的订单分别计费，不合并时段。get_total_cost返回所有已记录订单总金额，含已付与未付；unpaid返回未付金额。

pay_up_to只把end≤pay_time且尚未支付的整单标记已付，不按截止时间切分订单，返回None。重复付款或更早截止时间不得重复支付或撤销支付。付款后补录的订单初始仍为未付，下次适用的pay_up_to再结算。`add_driver`/record_delivery返回None，查询不得改变状态；空台账金额为0。

### 示例

```text
add_driver("d1",36)
record_delivery("d1",0,3600)
get_total_cost() -> 3600，unpaid() -> 3600
pay_up_to(3599) 后 unpaid() -> 3600
pay_up_to(3600) 后 unpaid() -> 0
再次pay_up_to(3600) 后 unpaid() -> 0，get_total_cost() -> 3600
```

## 解题思路与参考答案

这题的关键是给每单记一个已付标记，`pay_up_to` 只结算结束时间不超过截止时间、还没付过的整单，同一单就付不了两次。总工资在记单的时候累加，查询是 O(1)。

题来自 2025 年 4 月的 Rippling 店面，作者原话是给外卖员算薪水。一开始三个接口：`add_driver(driver_id, usd_hourly_rate)`；`record_delivery(driver_id, start_time, end_time)`，订单完成后才写入；`get_total_cost()`，返回平台要付的总工资。后面再加 `pay_up_to(pay_time)`。楼主在回复里说只付已经结束的单，因为 record 只在结束时写入，所以输入里不会有「start 在截止前、end 在截止后、人还在送」这种单。重复支付不能发生。有现成测试，明显的边界建议自己提出来，用 print 看。

2026 年 2 月另一则 SDE-2 电面（LeakCode 转的 Reddit）API 名字略不同：`addDriver`、`addDelivery(start, end)`、`getTotalCost`，然后 `payUpToTime` 和 `getCostToBePaid`。作者把未付写成总额减去已付，面试官说线性扫区间可以。这轮测试都过了，人还是被拒了。

一亩三分地后来的题库页把约束写得更满：Unix 秒，一单最长约 3 小时，工资等于时薪乘秒数再除以 3600，重叠时段各算各的，只标记结束时间不超过截止时间的整单。电话面那帖没写 3 小时和重叠，现场以面试官的测试为准。

实现时，我会把每单的结束时间、金额和已付状态放在一起；付款只改变状态，总额在记单时更新：

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

记单和查总额都是 O(1)，`pay_up_to` 和 `unpaid` 线性扫一遍所有单，面试官认可的就是这种线性扫。面试要是得用 double 才能对上他们的测试，就先按 double 写，口头说明生产里用整数分。`round` 往哪个方向舍（银行家舍入还是向上）要问一句，钱上的默认舍入不算对。

常见的错有两种。一种是把跨过截止时间的单按秒切开，可这帖的数据里根本没有这种单，写了切片，会和「只付已结束的整单」的测试不一致。另一种是每次付款都把所有已结束的单再加进已付金额，却没有已付标记，同一个截止时间调用两次，工资就翻倍了。

另外，2025 年 8 月投、11 月面的 SDE-1 走的是另一条流程：60 分钟 OA 两题，其中一题用到并查集；onsite 两道图，第二道是第一道的 follow-up；然后一道 document analyzer 的面向对象实现；最后 hiring manager 挖一个项目。那篇没有给出函数表，来源是 Medium 上的个人复盘，不单列成题。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

时薪 36 美元、送一小时应记 3600 分。检查付款截止时间的等号，以及重复付款不会重复扣减未付金额。

```python
payroll = Payroll()
payroll.add_driver("d1", 36)
payroll.record_delivery("d1", 0, 3600)
assert payroll.get_total_cost() == 3600
assert payroll.unpaid() == 3600
payroll.pay_up_to(3599)
assert payroll.unpaid() == 3600
payroll.pay_up_to(3600)
payroll.pay_up_to(3600)
assert payroll.unpaid() == 0
assert payroll.get_total_cost() == 3600
print("simple tests passed")
```

## 追问

**两单时间重叠怎么算？**
各付各的。题库页写的是重叠也各付各的，时薪按单计，不按人把时间并起来。电话面没说的话，先问再写。

**截止时间比上次还早呢？**
已付的单保持已付，更早的截止时间不能把钱退回去。

**单子在付款之后才补录怎么办？**
补录的单初始是未付。它的结束时间要是已经早于上次截止时间，下一次用同一个或更晚的时间付款就会把它付掉。除非面试官这么要求，不要在补录时自动当成已付。
