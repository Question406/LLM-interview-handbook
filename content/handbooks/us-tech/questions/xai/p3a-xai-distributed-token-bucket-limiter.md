---
id: p3a-xai-distributed-token-bucket-limiter
section: xai
order: 603
level: A
title: xAI：共享 token bucket：惰性补充与并发原子性
quick: >-
  我会按经过的时间惰性补令牌，封顶到 capacity，再检查并扣减；这三步必须在共享存储中原子完成。否则两台服务都读到剩 1
  个令牌，就可能各放行一次；时钟尽量用存储端时间，本地锁只用于单进程模拟。
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · xAI · distributed-token-bucket-limiter
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/distributed-token-bucket-limiter
    type: secondary
---

## 题目描述

实现一个按用户隔离的线程安全令牌桶限流器。每个用户有独立的满桶初始状态，令牌随时间补充但不能超过容量；同一用户的并发请求必须原子地完成补充、判断和扣减。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Store(capacity, rate)`：`capacity` 和 `rate` 都必须为正。
- `Store.allow(user, cost, now) -> bool`：令牌够就扣掉 `cost` 返回 `True`；不够返回 `False`，且不扣令牌。用户第一次请求时桶是满的，之后每秒补 `rate` 个，最多到 `capacity`。
- `cost` 必须为正，`now` 是非负秒数，并且对每个用户单调不减。
- 用多个线程共享同一个 `Store` 来模拟多个服务器。真实多机部署需要共享存储的原子事务，本地锁不能当成分布式实现。用户数不超过 $10^5$。

### 示例

```text
store = Store(capacity=5, rate=2)
store.allow("u", 5, 0) -> True     # 满桶 5 个，一次用完
store.allow("u", 1, 0) -> False    # 同一时刻没有补充
store.allow("u", 2, 1) -> True     # 1 秒后补回 2 个
```

## 解题思路与参考答案

我会把「补充、检查、扣减」放进共享存储的一次原子操作，按用户隔离桶。例如两台服务器同时读到还剩 1 个令牌，分开判断和写回就可能都通过，合计超发。下面先用共享 Store 和线程模拟这里需要的 atomicity。

## 题目

实现一个按用户限流的令牌桶，多个服务实例共同执行同一个限额。重点是令牌怎么按时间补充，以及多个实例同时扣令牌时怎么保证不超发。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

每个用户只保存剩余令牌数和上次更新时间。请求到来时再根据时间差补充，不需要后台定时器，计算为$\text{tokens} = \min(\text{capacity}, \text{tokens} + \Delta t \cdot \text{rate})$，再看够不够扣。这叫惰性补充。

多个实例共享限额时，「补充、检查、扣减」三步必须是一个原子操作。否则两个实例可能同时读到剩 1 个令牌，各自判断够用，结果多发了一次。进程内的锁只能保护同一个进程，挡不住另一台服务器，所以真实部署要把这段逻辑放进共享存储的事务或服务端脚本里执行，比如 Redis 的 Lua 脚本。

各实例的本地时钟可能有偏差，我会尽量使用存储端时间；练习中时间倒退直接拒绝。长期不活跃的用户状态可以过期清理，之后再来按新用户满桶处理，避免状态持续增长。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Store(capacity, rate)`：`capacity` 和 `rate` 都必须为正，否则抛 `ValueError`。
- `Store.allow(user, cost, now) -> bool`：令牌够就扣掉 `cost` 返回 `True`；不够返回 `False`，且不扣令牌。用户第一次请求时桶是满的，之后每秒补 `rate` 个，最多到 `capacity`。
- `cost` 必须为正，`now` 是非负秒数，并且对每个用户单调不减；违反时抛 `ValueError`。
- 用多个线程共享同一个 `Store` 来模拟多个服务器。真实多机部署需要共享存储的原子事务，本地锁不能当成分布式实现。用户数不超过 $10^5$。

### 输入输出示例

```text
store = Store(capacity=5, rate=2)
store.allow("u", 5, 0) -> True     # 满桶 5 个，一次用完
store.allow("u", 1, 0) -> False    # 同一时刻没有补充
store.allow("u", 2, 1) -> True     # 1 秒后补回 2 个
```

### 解题思路与正确性

锁覆盖了补充、检查和扣减三步，所以每次 `allow` 都可以看成在临界区内的某一瞬间整体完成，并发结果等价于某种串行顺序。在这个顺序下，每个用户的令牌数始终在 $[0, \text{capacity}]$ 之间，成功扣掉的总令牌数不会超过初始容量加上补充量。测试里 100 个并发请求抢 10 个令牌，恰好 10 次成功。

换成共享缓存时，逻辑不变：把这段代码放进一次 Redis Lua 脚本或事务，所有实例访问同一个 key，用服务端时间。

### 完整参考实现（Python 3）

```python
from threading import Lock


class Store:
    """所有服务共用的令牌桶存储；用一把锁模拟共享存储里的原子操作。"""

    def __init__(self, capacity, rate):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and rate must be positive")
        self.capacity = capacity
        self.rate = rate  # 每秒补充的令牌数
        self.buckets = {}  # user -> (剩余令牌, 上次更新时刻)
        self.lock = Lock()

    def allow(self, user, cost, now):
        """令牌够就扣掉 cost 并返回 True；不够返回 False，且不扣令牌。"""
        if cost <= 0:
            raise ValueError(f"cost must be positive, got {cost}")
        if now < 0:
            raise ValueError(f"now must be non-negative, got {now}")

        # 补充、检查、扣减必须在同一个临界区里完成，否则两个请求可能都看到足够的令牌
        with self.lock:
            tokens, last = self.buckets.get(user, (self.capacity, now))  # 新用户满桶
            if now < last:
                raise ValueError(f"time went backwards for {user!r}: {now} < {last}")
            tokens = min(self.capacity, tokens + (now - last) * self.rate)
            allowed = cost <= tokens
            if allowed:
                tokens -= cost
            self.buckets[user] = (tokens, now)
            return allowed
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert store.allow("u", 5, 0)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
from concurrent.futures import ThreadPoolExecutor


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


# 满桶 5 个，一次用完；同一时刻再要 1 个被拒；1 秒后补回 2 个
store = Store(5, 2)
assert store.allow("u", 5, 0)
assert not store.allow("u", 1, 0)
assert store.allow("u", 2, 1)

# 补充不超过容量
assert store.allow("v", 5, 100)
assert not store.allow("v", 6, 1000)

# 时间倒退和非法 cost
expect_value_error(store.allow, "u", 1, 0)
expect_value_error(store.allow, "u", 0, 5)

# 8 个线程并发抢同一个用户的 10 个令牌，恰好 10 次成功
store = Store(10, 1)
with ThreadPoolExecutor(8) as pool:
    results = list(pool.map(lambda _: store.allow("u", 1, 0), range(100)))
assert sum(results) == 10
```

### 复杂度与追问

设用户数为 U。每次 `allow` 是 O(1)，状态占 O(U) 空间。

如果追问单锁的瓶颈：一把锁会让所有用户的请求串行。不同用户之间互不影响，可以按用户哈希分片，每片一把锁；在 Redis 里同一用户的 key 落在同一个分片上，天然只锁这一个 key。

如果追问和固定窗口限流的区别：令牌桶按时间连续补充，允许短时间突发到 `capacity`；固定窗口只在 window boundaries 清零，窗口交界处可能放过两倍的请求。这份实现要求时间单调，不适合重放乱序的历史请求。

## 相关题

- [[xai-rate-limiter]]：同为 xAI 的令牌桶编码题，多了一层全局桶，两层都够才一起扣，重点是多租户公平而不是跨实例原子性。
- [[anthropic-rate-limit]]：令牌桶和滑动窗口的系统设计版，同时限请求数和 token 数，并讲 Redis 原子扣减和 fail closed。
- [[p3a-xai-rate-limiter-design]]：xAI 的非编程版，入口和出站两套限流，其中「每台机器各分一份行不行」就是本题共享限额的问题。
