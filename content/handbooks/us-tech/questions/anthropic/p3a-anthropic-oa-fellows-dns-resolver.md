---
id: p3a-anthropic-oa-fellows-dns-resolver
section: anthropic
order: 615
level: A
title: "Anthropic：Fellows DNS：别名、回退、环与缓存"
quick: "我会沿 CNAME 链解析，用访问集合检测别名环，并缓存最终 IP。缓存 TTL 取链上的最小值；这份练习不缓存失败，避免把一次临时故障长时间当成域名不存在。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · oa-fellows-dns-resolver"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/oa-fellows-dns-resolver
    type: secondary
---

## 题目描述

实现内存中的简化 DNS 解析器，支持 A 记录、CNAME 别名、按 TTL 过期的成功结果缓存，以及本地记录缺失时的查询回退。不进行真实网络解析；域名不存在属于正常业务结果，不能作为成功结果写入缓存。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Resolver(records, fallback=None)`：`records[name] = (kind, value, ttl)`，`kind` 是 `"A"` 或 `"CNAME"`。名字统一 casefold 并去掉末尾的 `.`。
- `resolve(name, now) -> str`：返回 IPv4 地址字符串。A 记录的值必须是合法 IPv4 地址；CNAME 的值按完整域名处理，没有搜索域。
- 缓存原始查询名对应的最终 IP，过期时刻是 `now` 加上整条链上最小的 TTL，`now >= 过期时刻` 时失效。
- 本地没有记录时调用 `fallback(name)`，它返回 `(ip, ttl)`，返回 `None` 表示域名不存在，此时抛 `KeyError`。失败结果不缓存。
- records 最多1000条，TTL 均有限且非负，CNAME 无环，记录及 fallback 的 IPv4 均合法；同一实例 resolve 的 now 单调不减。缓存 TTL 为0时不跨调用复用。

### 输入输出示例

```text
r = Resolver({"a": ("CNAME", "b", 5), "b": ("A", "1.2.3.4", 10)})
r.resolve("A.", 0) -> "1.2.3.4"
r.records["b"] = ("A", "5.6.7.8", 10)
r.resolve("a", 4) -> "1.2.3.4"
r.resolve("a", 5) -> "5.6.7.8"
```

## 解题思路与参考答案

## 题目

在一个固定的测试框架里，分步骤实现一个简化的 DNS 解析器：先查直接的地址记录，再支持沿别名（CNAME）继续解析，然后加上缓存和本地查不到时的回退查询。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会从查询名开始逐条查记录：遇到 A 记录就拿到地址，遇到 CNAME 就继续查别名指向的名字。这次查询用一个集合记录走过的名字，再次遇到同一个名字就报别名成环，避免解析一直循环。

缓存时，成功和失败要用不同的策略。成功结果按 TTL 缓存；失败（网络超时、回退服务出错）不应该被当成「域名不存在」长期缓存下来，否则一次临时故障会让这个域名在很长时间里都解析不了。真正的 NXDOMAIN 可以做短时间的负缓存，但这份练习为了简单，所有失败都不缓存。

还有几件事要先和面试官统一：什么情况下触发回退，别名链最多允许多深，以及多个请求同时查同一个名字时要不要合并成一次查询。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Resolver(records, fallback=None)`：`records[name] = (kind, value, ttl)`，`kind` 是 `"A"` 或 `"CNAME"`。名字统一 casefold 并去掉末尾的 `.`。
- `resolve(name, now) -> str`：返回 IPv4 地址字符串。A 记录的值必须是合法 IPv4 地址；CNAME 的值按完整域名处理，没有搜索域。
- 缓存原始查询名对应的最终 IP，过期时刻是 `now` 加上整条链上最小的 TTL，`now >= 过期时刻` 时失效。查询时钟单调不减，倒退时抛 `ValueError`。
- 本地没有记录时调用 `fallback(name)`，它返回 `(ip, ttl)`，返回 `None` 表示域名不存在，此时抛 `KeyError`。失败结果不缓存。
- 别名成环、TTL 为负或记录类型不支持时抛 `ValueError`。最多 1000 条记录。

### 输入输出示例

```text
records = {a: (CNAME, b, 5), b: (A, 1.2.3.4, 10)}
resolve("A.", 0)   -> "1.2.3.4"   # 缓存到时刻 5
# 之后把 b 改成 5.6.7.8
resolve("a", 4)    -> "1.2.3.4"   # 还在缓存期内
resolve("a", 5)    -> "5.6.7.8"   # 缓存过期，重新沿链解析
```

### 解题思路与正确性

`_follow_chain` 每次只沿当前名字的记录前进一步，用 `seen` 集合检测这一次查询里是否回到了走过的名字。链上每经过一条记录，就把 TTL 更新为目前的最小值。

缓存的是原始查询名到最终 IP 的映射，TTL 取整条链的最小值。如果只用终点 A 记录的 TTL，一条 TTL 很短的 CNAME 会被 A 记录较长的 TTL「延长」，别名改了之后，缓存还会继续返回旧地址。

出错时直接抛异常，不写缓存，所以一次临时失败不会让这个名字一直被当成不存在。

### 完整参考实现（Python 3）

```python
import ipaddress


def normalize(name):
    """域名不区分大小写，末尾的 "." 可有可无。"""
    return name.casefold().rstrip(".")


def parse_ipv4(text):
    return str(ipaddress.IPv4Address(text))  # 非法地址会抛 ValueError


class Resolver:
    """简化的 DNS 解析器：支持 A 和 CNAME 记录、TTL 缓存和 fallback 查询。

    records[name] = (kind, value, ttl)，kind 是 "A" 或 "CNAME"。
    fallback(name) 在本地没有记录时调用，返回 (ip, ttl)，返回 None 表示域名不存在。
    """

    def __init__(self, records, fallback=None):
        self.records = {normalize(name): record for name, record in records.items()}
        self.fallback = fallback
        self.cache = {}  # 原始查询名 -> (ip, 过期时刻)
        self.last_now = float("-inf")

    def resolve(self, name, now):
        """返回 name 的 IPv4 地址。不存在时抛 KeyError，CNAME 成环或数据非法时抛 ValueError。"""
        if now < self.last_now:
            raise ValueError(f"time went backwards: {now} < {self.last_now}")
        self.last_now = now
        query = normalize(name)

        cached = self.cache.get(query)
        if cached is not None:
            ip, expires_at = cached
            if now < expires_at:
                return ip

        ip, ttl = self._follow_chain(query)
        # 只缓存成功结果；失败不写缓存，暂时的网络错误不会变成长期的「不存在」
        self.cache[query] = (ip, now + ttl)
        return ip

    def _follow_chain(self, query):
        """沿 CNAME 链走到 A 记录，返回 (ip, 整条链上最小的 TTL)。"""
        seen = set()
        current = query
        ttl = float("inf")
        while True:
            if current in seen:
                raise ValueError(f"CNAME cycle at {current!r}")
            seen.add(current)

            record = self.records.get(current)
            if record is None:
                return self._ask_fallback(current, ttl)

            kind, value, record_ttl = record
            if record_ttl < 0:
                raise ValueError(f"negative TTL for {current!r}")
            ttl = min(ttl, record_ttl)
            if kind == "A":
                return parse_ipv4(value), ttl
            if kind != "CNAME":
                raise ValueError(f"unsupported record type: {kind!r}")
            current = normalize(value)

    def _ask_fallback(self, name, ttl_so_far):
        answer = self.fallback(name) if self.fallback else None
        if answer is None:
            raise KeyError(name)
        ip, fallback_ttl = answer
        if fallback_ttl < 0:
            raise ValueError(f"negative TTL from fallback for {name!r}")
        return parse_ipv4(ip), min(ttl_so_far, fallback_ttl)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert resolver.resolve("A.", 0) == "1.2.3.4"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_error(error, fn, *args):
    try:
        fn(*args)
    except error:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise {error.__name__}")

# 缓存 TTL 取整条链的最小值：CNAME 的 5，而不是 A 记录的 10
resolver = Resolver({"a": ("CNAME", "b", 5), "b": ("A", "1.2.3.4", 10)})
assert resolver.resolve("A.", 0) == "1.2.3.4"
assert resolver.cache["a"][1] == 5

# 缓存期内看不到记录变化，到期后重新查链
resolver.records["b"] = ("A", "5.6.7.8", 10)
assert resolver.resolve("a", 4) == "1.2.3.4"
assert resolver.resolve("a", 5) == "5.6.7.8"

# CNAME 指向自己
expect_error(ValueError, Resolver({"a": ("CNAME", "a", 1)}).resolve, "a", 0)

# 本地没有记录时走 fallback；fallback 返回 None 表示不存在，且失败不缓存
answers = {"ext": ("9.9.9.9", 3)}
with_fallback = Resolver({"x": ("CNAME", "ext", 7)}, fallback=answers.get)
assert with_fallback.resolve("x", 0) == "9.9.9.9"
assert with_fallback.cache["x"][1] == 3
expect_error(KeyError, with_fallback.resolve, "missing", 1)
assert "missing" not in with_fallback.cache

expect_error(ValueError, resolver.resolve, "a", 4)  # 时钟倒退
```

### 复杂度与追问

设别名链长度为 L。缓存命中是 O(1)，未命中时沿链解析是 O(L)。空间是 O(记录数 + 不同查询名数)。

追问「多线程同时解析」：缓存要加锁保护；同一个名字的并发查询应合并成一次（single-flight），其他请求等这一次的结果。但不能拿着全局锁去调用很慢的网络 fallback，否则所有查询都会被这一次网络请求堵住。常见做法是只在读写缓存和登记「正在查询」时短暂持锁，网络请求在锁外进行。
