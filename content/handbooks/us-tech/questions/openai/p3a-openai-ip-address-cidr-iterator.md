---
id: p3a-openai-ip-address-cidr-iterator
section: openai
order: 615
level: A
title: "OpenAI：IPv4 / CIDR：解析、范围和双向迭代"
quick: "把 IPv4 转成 32 位整数，CIDR 用网络起点和地址数表示，无需展开地址列表。游标保存下一个返回的偏移，next 返回再加一、prev 先减一再返回，范围检查同样在整数区间上做。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · ip-address-cidr-iterator"
    url: https://www.1point3acres.com/interview/problems/company/openai/ip-address-cidr-iterator
    type: secondary
---

## 题目描述

实现 IPv4 地址与整数的互转，以及可前进、后退、保存状态的 CIDR 地址迭代器。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `ip_to_int(text)` / `int_to_ip(value)`：IPv4 点分十进制和整数互转。地址必须是四段 0 到 255 的十进制数，不能有前导 0。
- `CIDR(text)`：解析 CIDR，主机位不为 0 时规范化成网络地址，比如 `10.0.0.1/30` 视为 `10.0.0.0/30`。
- `next()`：返回当前偏移处的地址并前进；已经到末尾时抛 `StopIteration`。
- `prev()`：先后退一步再返回该地址；已经在起点时抛 `StopIteration`。
- `contains(address)`：判断地址是否在范围内。网络地址和广播地址都算在内，不按可分配主机过滤。
- `get_state()` / `set_state(pos)`：状态是下一个要返回的偏移，要求 $0 \le pos \le$ 地址数。
- 合法整数地址范围为 `[0, 2^32-1]`，CIDR 前缀长度为 `[0,32]`；不能预先枚举整个 `/0`。

### 输入输出示例

```text
cidr = CIDR("10.0.0.1/30")    # 规范化为 10.0.0.0 - 10.0.0.3
cidr.next()                   -> "10.0.0.0"
cidr.next()                   -> "10.0.0.1"
cidr.prev()                   -> "10.0.0.1"
cidr.contains("10.0.0.4")     -> False
```

`prev` 返回的是刚才 `next` 返回过的那个地址，因为两者共用「下一个要返回的偏移」这一个状态。

## 解题思路与参考答案

我会把 IPv4 转成 32 位无符号整数，用起点、长度和偏移实现 CIDR 迭代器。IPv4 的四段分别对应整数的四个字节。把地址转成整数之后，CIDR `a.b.c.d/p` 就是一个连续的整数区间：起点是把低 $32 - p$ 位清零后的值，长度是 $2^{32-p}$。迭代器只需要记住起点、长度和当前偏移，不用把地址列表展开，`/0` 也只是一个很大的长度。

## 题目

分阶段实现 IPv4 地址和 CIDR 范围的相关操作：地址和整数互相转换，解析 CIDR 得到地址范围，判断地址是否在范围内，再在范围上实现一个可以前进、后退并能保存和恢复状态的迭代器。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

要校验的边界：

- 每段必须是 0 到 255 的十进制数，四段齐全，不能有前导 0；
- 前缀长度 0 和 32 都合法，`/32` 只有一个地址，`/0` 覆盖全部地址；
- 迭代到最后一个地址 `255.255.255.255` 之后要正确耗尽，不能溢出。

后退接口最容易出歧义：`prev` 返回的是「上一个返回过的地址」还是「当前位置的前一个」？这里统一用一个「下一个要返回的偏移」作为状态，`next` 返回它再加一，`prev` 先减一再返回。保存和恢复也用同一个偏移，几种操作就不会互相矛盾。动手前值得和面试官确认这一点，以及网络地址和广播地址算不算在范围内。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `ip_to_int(text)` / `int_to_ip(value)`：IPv4 点分十进制和整数互转。地址必须是四段 0 到 255 的十进制数，不能有前导 0，否则抛 `ValueError`。
- `CIDR(text)`：解析 CIDR，主机位不为 0 时规范化成网络地址，比如 `10.0.0.1/30` 视为 `10.0.0.0/30`。
- `next()`：返回当前偏移处的地址并前进；已经到末尾时抛 `StopIteration`。
- `prev()`：先后退一步再返回该地址；已经在起点时抛 `StopIteration`。
- `contains(address)`：判断地址是否在范围内。网络地址和广播地址都算在内，不按可分配主机过滤。
- `get_state()` / `set_state(pos)`：状态是下一个要返回的偏移，要求 $0 \le pos \le$ 地址数，否则抛 `ValueError`。
- 解析用标准库 `ipaddress`；不能枚举整个 `/0`。

### 输入输出示例

```text
cidr = CIDR("10.0.0.1/30")    # 规范化为 10.0.0.0 - 10.0.0.3
cidr.next()                   -> "10.0.0.0"
cidr.next()                   -> "10.0.0.1"
cidr.prev()                   -> "10.0.0.1"
cidr.contains("10.0.0.4")     -> False
```

`prev` 返回的是刚才 `next` 返回过的那个地址，因为两者共用「下一个要返回的偏移」这一个状态。

### 解题思路与正确性

`ipaddress.IPv4Network(text, strict=False)` 负责解析和规范化，得到网络起点 `start` 和地址数 `size`。范围就是整数区间 $[start, start + size)$，`contains` 只做两次整数比较。

游标 `pos` 始终满足 $0 \le pos \le size$。`next` 只在 $pos < size$ 时返回并加一，`prev` 只在 $pos > 0$ 时减一并返回，所以两者都不会越出区间。地址由 `start + pos` 算出来，不需要任何列表。

### 完整参考实现（Python 3）

```python
import ipaddress


def ip_to_int(text):
    """'10.0.0.1' -> 167772161；格式非法（段越界、前导 0 等）时抛 ValueError。"""
    return int(ipaddress.IPv4Address(text))


def int_to_ip(value):
    return str(ipaddress.IPv4Address(value))


class CIDR:
    """CIDR 范围上的双向迭代器。

    状态 pos 是「下一个要由 next 返回的地址偏移」，取值 0..size：
    next 返回 pos 再加一，prev 先减一再返回，两者用同一个位置定义。
    """

    def __init__(self, text):
        network = ipaddress.IPv4Network(text, strict=False)  # 主机位清零，规范化成网络地址
        self.start = int(network.network_address)
        self.size = network.num_addresses  # 2 ** (32 - prefix)，/0 也只存一个整数
        self.pos = 0

    def next(self):
        if self.pos >= self.size:
            raise StopIteration
        address = int_to_ip(self.start + self.pos)
        self.pos += 1
        return address

    def prev(self):
        if self.pos == 0:
            raise StopIteration
        self.pos -= 1
        return int_to_ip(self.start + self.pos)

    def contains(self, address):
        return self.start <= ip_to_int(address) < self.start + self.size

    def get_state(self):
        return self.pos

    def set_state(self, pos):
        if type(pos) is not int or not 0 <= pos <= self.size:
            raise ValueError(f"invalid state: {pos!r}")
        self.pos = pos
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert ip_to_int("10.0.0.1") == 10 * 2 ** 24 + 1` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_error(error, fn, *args):
    try:
        fn(*args)
    except error:
        return
    raise AssertionError(f"{fn.__name__} should raise {error.__name__}")

# 地址与整数互转
assert ip_to_int("10.0.0.1") == 10 * 2 ** 24 + 1
assert int_to_ip(2 ** 32 - 1) == "255.255.255.255"
expect_error(ValueError, ip_to_int, "256.0.0.1")
expect_error(ValueError, ip_to_int, "01.2.3.4")

# 10.0.0.1/30 规范化为 10.0.0.0 - 10.0.0.3，含网络地址和广播地址
cidr = CIDR("10.0.0.1/30")
assert cidr.next() == "10.0.0.0"
assert cidr.next() == "10.0.0.1"
assert cidr.prev() == "10.0.0.1"
assert cidr.contains("10.0.0.3")
assert not cidr.contains("10.0.0.4")

# 保存状态后前进，再恢复，能重放同一项
state = cidr.get_state()
assert cidr.next() == "10.0.0.1"
cidr.set_state(state)
assert cidr.next() == "10.0.0.1"

# /0 不枚举，直接跳到最后一个地址
everything = CIDR("0.0.0.0/0")
everything.set_state(everything.size - 1)
assert everything.next() == "255.255.255.255"

# /32 只有一个地址，取完后 next 耗尽；回到起点后 prev 耗尽
single = CIDR("1.2.3.4/32")
assert single.next() == "1.2.3.4"
expect_error(StopIteration, single.next)
assert single.prev() == "1.2.3.4"
expect_error(StopIteration, single.prev)

# 非法状态
expect_error(ValueError, single.set_state, 2)
```

### 复杂度与追问

IPv4 地址定长，所有操作都是 O(1) 时间、O(1) 空间，和前缀长度无关。

- 不让用 `ipaddress` 怎么办？自己按 `.` 切成四段，检查段数、每段是纯数字、没有前导 0、值在 0 到 255，然后用 `(a << 24) | (b << 16) | (c << 8) | d` 拼成整数；网络起点是 `ip & mask`，其中 `mask = (0xFFFFFFFF << (32 - p)) & 0xFFFFFFFF`。
- 要支持 IPv6 吗？IPv6 是 128 位，不能直接塞进这套 32 位实现，需要单独的解析和更宽的整数（Python 的 int 本身没有位宽限制）。
