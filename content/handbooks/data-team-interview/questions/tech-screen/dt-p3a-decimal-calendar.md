---
id: dt-p3a-decimal-calendar
section: tech-screen
order: 72
level: A
title: Apple Foundation Model 原帖扩展：小数时间预约的最大重叠数
quick: >-
  小数端点不能直接沿用整数区间算法里 endpoint 加一减一的做法。先明确时间精度和半开区间语义；本练习从字符串解析
  Decimal，在起点加一、终点减一，并按同一端点的净变化做扫描。
companies:
  - apple
tags:
  - Apple
  - 一亩三分地原帖核对
  - AFM 专项 2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-26'
sources:
  - title: 果家foundation model电面面经，候选人原帖，Chrome核对2026-10-26
    url: 'https://www.1point3acres.com/bbs/thread-1145559-1-1.html'
    type: interview
  - title: LeetCode 732 My Calendar III，题型解释参考
    url: 'https://leetcode.com/problems/my-calendar-iii/description/'
    type: primary
  - title: Python decimal documentation
    url: 'https://docs.python.org/3/library/decimal.html'
    type: primary
---

## 题目描述

### 原帖核对与练习约定

- 原帖：[果家 foundation model 电面面经，求米~~~](https://www.1point3acres.com/bbs/thread-1145559-1-1.html)，发帖时间为页面显示的 2025-09-13 22:37:42。
- 采集日期：2026-10-26。Chrome 中可见主楼；相关段落显示当前会话已经可以浏览，无绕过访问限制。
- 原帖披露：作者明确面试 Foundation Model team，编程轮出现与“漆傘贰”类似、但时间是小数的题。“漆傘贰”在这里按 LC 732《My Calendar III》理解；这是题号解释。
- **本题练习约定**：将其重构成在线加入半开区间、返回历史峰值重叠数的接口。原帖没有披露端点类型、精度、规模或标准答案；以下 Decimal 字符串接口与扫描线解法均为手册设计。

### 输入与接口

实现 `DecimalCalendar()` 及 `book(start: str, end: str) -> int`。初始为空。start/end 为非负有限十进制数字串，不使用科学计数法，最多 30 个数字字符；保证 start 小于 end。最多调用 400 次。输入示例为 `'0.10'`、`'12.375'`。

### 输出与约束

每次添加区间 `[start,end)`，返回截至本次加入后，任一时间点同时覆盖的区间数量最大值。终点等于另一区间起点时不重叠。重复预约视为不同事件，必须分别计数。不删除事件，不将输入先转成 float，不设任意 epsilon。

### 示例

```text
calendar=DecimalCalendar()
book('0.1','0.3')  -> 1
book('0.30','0.4') -> 1
book('0.2','0.35') -> 2
book('0.10','0.30')-> 3
```

## 解题思路与参考答案

在每个起点记录 +1，终点记录 -1。先聚合同一 Decimal 端点的变化，再按升序累加并取峰值。聚合使一个事件结束、另一个事件开始时没有虚假的瞬间双重计数。

直接从十进制字符串构造 Decimal，`'0.3'` 与 `'0.30'` 表示相同数值。代码只比较 Decimal 端点，计数是整数运算，不做可能受精度影响的时间加减。

```python
from decimal import Decimal


class DecimalCalendar:
    def __init__(self):
        self.delta = {}

    def book(self, start, end):
        left, right = Decimal(start), Decimal(end)
        self.delta[left] = self.delta.get(left, 0) + 1
        self.delta[right] = self.delta.get(right, 0) - 1
        active = peak = 0
        for time in sorted(self.delta):
            active += self.delta[time]
            peak = max(peak, active)
        return peak
```

第 n 次加入时最多有 2n 个端点，时间为 $O(n\log n)$，存储为 $O(n)$；N 次总成本为 $O(N^2\log N)$。对于本题约定的 400 次调用，这是容易解释和验证的 baseline；原帖未披露规模，不能声称满足原面试全部性能要求。

## 简单测试怎么写

将实现和以下测试保存到 `solution.py`，运行 `python3 solution.py`。先检查相邻半开区间，再检查同值的不同小数写法、重复事件和非常接近但不同的端点。

```python
calendar = DecimalCalendar()
assert calendar.book('0.1', '0.3') == 1
assert calendar.book('0.30', '0.4') == 1
assert calendar.book('0.2', '0.35') == 2
assert calendar.book('0.10', '0.30') == 3
nested = DecimalCalendar()
assert nested.book('1.0', '10.0') == 1
assert nested.book('2.25', '9.75') == 2
assert nested.book('3.5', '8.5') == 3
close = DecimalCalendar()
assert close.book('0.1000000000000000000001', '0.1000000000000000000002') == 1
assert close.book('0.1000000000000000000002', '0.1000000000000000000003') == 1
```

## 面试追问

**为什么不能直接把小数乘一千变整数？** 只有时间精度已被明确限制为千分之一时才正确。若端点有更多有效位，四舍五入可能把原本分开的事件合并；应先询问业务精度。

**有了 float 端点还能恢复原始十进制吗？** 一般不能凭空恢复。若输入本来是 float，应明确按浮点值比较还是按业务单位 quantization；不要声称 `Decimal(float_value)` 就消除了已有误差。

**规模很大怎么办？** 离线已知端点可做坐标压缩；真正在线可用按端点排序的平衡树，节点维护子树 delta 总和及最大 prefix sum。整数动态线段树不能不加说明地用 `mid+1` 覆盖任意小数域。
