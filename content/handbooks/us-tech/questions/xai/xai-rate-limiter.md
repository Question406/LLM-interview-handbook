---
id: xai-rate-limiter
section: xai
order: 3
level: A
title: xAI coding：API rate limiter，多租户公平和突发
quick: >-
  我会用懒填充令牌桶，每个 key
  只存余额和时间戳，请求到来再按经过的时间补额度。多租户同时检查用户桶和全局桶，都够才原子扣减；配额隔离之外，排队还要单独按权重调度，才能处理公平和突发。
tags:
  - 完整编程练习
  - xAI
  - Rate Limiter
  - Token Bucket
  - Coding
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Get a Job at xAI — Interview Process and Top Questions
    url: 'https://www.tryexponent.com/blog/xai-interview-process'
    type: secondary
  - title: xAI Software Engineer Interview Guide
    url: 'https://www.tryexponent.com/guides/xai-software-engineer-interview'
    type: secondary
  - title: xAI Interview Questions from Candidate Reports
    url: 'https://aceoffer.app/interviews/xai'
    type: secondary
  - title: Practice xAI Mock Interviews
    url: 'https://igotanoffer.com/en/mock-interviews/company/xai'
    type: secondary
---

## 题目描述

实现每用户与全局共同生效的令牌桶限流器，保证并发请求的扣费原子性。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`Limiter(user_capacity,user_rate,global_capacity,global_rate)` 接收有限正数。用户桶首次出现时为满桶，全局桶初始也为满桶；每桶按经过时间乘对应 rate 补充令牌，最多补至 capacity。

`allow(user,cost,now)` 返回是否允许，cost 为正数，now 非负且全部用户的调用时间全局单调不减。仅当该用户桶与全局桶都足够时才允许，并同时各扣 cost；拒绝时两桶均不扣消费令牌，正常的时间补充仍然有效。用户桶互相独立，全局桶由所有用户共享。检查与双桶扣减必须线程安全，不维护等待队列。

### 示例

```text
user_capacity=2,user_rate=1,global_capacity=3,global_rate=1。
allow("a",2,0)=True
allow("a",1,0)=False
allow("b",1,0)=True
allow("b",1,0)=False
allow("b",1,1)=True
```

## 解题思路与参考答案

我会先写懒填充令牌桶，再叠每租户和全局两层限制。例如用户桶不够时，就算全局桶还有余额，也要拒绝且两个桶都不扣，避免失败请求消耗额度。分布式扩展时继续保持这次检查与扣减的原子性。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3，只用标准库。

### 题面、接口与约束

- `Limiter(user_capacity, user_rate, global_capacity, global_rate)`：每个用户一个令牌桶，平台再共用一个全局桶。四个参数都必须是有限正数，否则抛 `ValueError`。两种桶初始都是满的。
- `Limiter.allow(user, cost, now) -> bool`：按经过的时间给两个桶惰性补充 token（不超过容量），两个桶都够 `cost` 时同时扣款并返回 `True`；任意一个不够就返回 `False`，两个桶都不扣。
- `cost` 是有限正数，`now` 是有限非负数，并且在整个 limiter 上（跨用户）单调不减；违反时抛 `ValueError`。
- 多线程共享同一个实例时，检查和扣款必须是原子的。
- 不排队；每用户配额隔离不等于加权公平调度（见复杂度与追问）。

### 输入输出示例

```text
Limiter(user_capacity=2, user_rate=1, global_capacity=3, global_rate=1)
allow("a", 2, now=0)  -> True    # 用户桶 a: 0，全局: 1
allow("a", 1, now=0)  -> False   # a 的桶不够，全局桶不扣
allow("b", 1, now=0)  -> True    # 全局还剩 1，刚好够
allow("b", 1, now=0)  -> False   # 全局用完
allow("b", 1, now=1)  -> True    # 过了 1 秒，两个桶各补 1
```

### 解题思路与正确性

每个桶只存「余额」和「上次更新时间」。请求到来时先按 $\Delta t \times \text{rate}$ 补充并封顶，再判断够不够，所以不需要后台线程。

两个桶的补充、检查和扣款都在同一把锁里完成，而且只有两个桶都够时才一起扣。如果先扣全局、再发现用户桶不够，就会出现「全局扣了、用户被拒、额度蒸发」。被拒的请求仍然把补充后的余额和时间写回去，只是不扣费，这不影响结果，因为补充只依赖时间差。

时间要求在整个 limiter 上单调，是因为全局桶被所有用户共享：如果允许用户 a 在 `now=5` 之后，用户 b 又用 `now=3` 调用，全局桶的时间就会倒退。

### 完整参考实现（Python 3）

```python
import math
from threading import Lock


class Limiter:
    """每用户令牌桶 + 全局令牌桶，惰性补充；两个桶都够才同时扣款。线程安全。"""

    def __init__(self, user_capacity, user_rate, global_capacity, global_rate):
        params = (user_capacity, user_rate, global_capacity, global_rate)
        if any(not math.isfinite(value) or value <= 0 for value in params):
            raise ValueError(
                f"capacities and rates must be positive and finite, got {params}"
            )
        self.user_capacity = user_capacity
        self.user_rate = user_rate
        self.global_capacity = global_capacity
        self.global_rate = global_rate
        self.user_buckets = {}  # user -> (tokens, last_refill_time)
        self.global_tokens = global_capacity
        self.last_time = None  # 上一次调用的 now，整个 limiter 共用
        self.lock = Lock()

    def allow(self, user, cost, now):
        """补充两个桶后，两个都够 cost 才扣款并返回 True；否则不扣任何桶，返回 False。"""
        if not math.isfinite(cost) or cost <= 0:
            raise ValueError(f"cost must be positive and finite, got {cost}")
        if not math.isfinite(now) or now < 0:
            raise ValueError(f"now must be non-negative and finite, got {now}")
        with self.lock:
            if self.last_time is not None:
                if now < self.last_time:
                    raise ValueError(f"time went backwards: {now} < {self.last_time}")
                elapsed = now - self.last_time
                self.global_tokens = min(
                    self.global_capacity,
                    self.global_tokens + elapsed * self.global_rate,
                )
            self.last_time = now
            tokens, last_refill = self.user_buckets.get(user, (self.user_capacity, now))
            tokens = min(
                self.user_capacity, tokens + (now - last_refill) * self.user_rate
            )
            accepted = tokens >= cost and self.global_tokens >= cost
            if accepted:
                tokens -= cost
                self.global_tokens -= cost
            self.user_buckets[user] = (tokens, now)
            return accepted
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert limiter.allow("a", 2, 0)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
from concurrent.futures import ThreadPoolExecutor


def expect_error(error_type, fn, *args):
    try:
        fn(*args)
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


limiter = Limiter(2, 1, 3, 1)

# 用户桶用完后被拒
assert limiter.allow("a", 2, 0)
assert not limiter.allow("a", 1, 0)

# 被拒的请求没有消耗全局额度，b 还能用掉剩下的 1
assert limiter.allow("b", 1, 0)
assert not limiter.allow("b", 1, 0)

# 时间推进后两个桶都补充
assert limiter.allow("b", 1, 1)

# 补充封顶在容量：空闲很久后也只能用到 user_capacity
assert limiter.allow("a", 2, 100)
assert not limiter.allow("a", 3, 100)

# 时间倒退报错
expect_error(ValueError, limiter.allow, "a", 1, 99)

# 非法参数和非法请求
expect_error(ValueError, Limiter, 0, 1, 1, 1)
expect_error(ValueError, Limiter, 1, float("inf"), 1, 1)
expect_error(ValueError, limiter.allow, "a", 0, 100)
expect_error(ValueError, limiter.allow, "a", 1, float("nan"))

# 全局桶限制所有用户的总和
shared = Limiter(5, 1, 3, 1)
results = [shared.allow(f"user-{i}", 1, 0) for i in range(5)]
assert results == [True, True, True, False, False]

# 并发：100 个线程同时请求，只放行全局容量 7 次
concurrent = Limiter(10, 1, 7, 1)
with ThreadPoolExecutor(8) as pool:
    accepted = sum(pool.map(lambda _: concurrent.allow("u", 1, 0), range(100)))
assert accepted == 7
```

### 复杂度与追问

设用户数为 $U$。每次 `allow` 是 $O(1)$，空间 $O(U)$。

- 追问「一把锁会不会成为瓶颈」：单锁保证单机正确，但所有用户串行。可以把用户桶按 key 分片加锁，全局桶单独用原子操作；分布式时，两个桶的检查和扣款必须放进同一个原子操作（比如一段 Redis Lua 脚本）。
- 追问「这算公平吗」：这段代码只保证每个用户的配额互相隔离。Weighted Fair Queueing 这类加权公平调度需要单独的调度策略，token bucket 不会自动提供。

## 题怎么来的

公开汇总里这道题有 coding 和 design 两种形态：先实现单个 URL 或单个 key 的限流，再加复合规则、按 payload 计费和多租户配额。Exponent 把 rate limiter 和 KV 事务并列为 xAI 的高频应用题，AceOffer 写过 lazy-refill 令牌桶。来源：本手册题型整理，练习目标是「写出能跑的类，并把公平和突发讲清楚」。口味和 `xai-kv-txn` 一样：考的是共享状态、时钟和并发，不是 LeetCode 花样。

## 先写懒填充桶，再谈分布式

生产系统不会每毫秒给所有用户加 token。每个 key 只存 `(tokens, last_ts)`，请求来了再算：

$$
t \leftarrow \min(\mathrm{burst},\; t + r\cdot\Delta),\qquad
\text{若 } t \ge c \text{ 则扣 } c \text{，否则拒绝}.
$$

$r$ 是稳态速率，$\Delta$ 是距上次更新的时间，$c$ 是本次代价（默认 1，按 payload 计费时可以是字节数），burst 是桶深。时钟用注入的 `now` 函数，单测才能复现。单个桶的最小写法：

```python
class TokenBucket:
    """单个懒填充令牌桶；now 是注入的时钟函数，便于测试。"""

    def __init__(self, rate, burst, now):
        self.rate = rate
        self.burst = burst
        self.now = now
        self.tokens = burst
        self.last_ts = now()

    def allow(self, cost=1) -> bool:
        current = self.now()
        elapsed = max(0.0, current - self.last_ts)
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_ts = current
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True
```

常见误区：

- 另起线程定时 refill。OA 里很难测，还会和请求线程抢状态。
- 用固定窗口计数。window boundaries 处可以出现两倍的突发。
- 用漏桶。漏桶只做平滑，不能「先攒再爆」，和产品说的 burst 对不上。

滑动窗口更准，但状态更重，留作 follow-up。

## 多租户的额度和公平怎么分开处理

API 网关常见两层限制：平台总 QPS，以及每个 consumer / API key 的配额。两个桶都通过才放行。先扣哪一层要事先规定，失败要回滚，参考实现的做法是先检查两层、都够了再一起扣。

复合规则（比如 URL A 和 B 共用一笔预算，同时各自又有上限）用规则表处理：一次请求列出命中的所有 bucket id，按 id 排序后加锁，避免 AB/BA 死锁。这和 `xai-kv-txn` 里按 key 排序加锁是同一个手法。

公平不等于平均分。大客户权重更大，但不能让它把小客户的突发窗口吃光。可以从三方面讲：

- 加权公平：每个租户一个桶，全局另有一个令牌池或队列。权重 $w_i$ 决定借还的速度，而不是让 burst 变成无限。
- 突发：burst 只覆盖短暂的尖峰（重试风暴、页面刷新），稳态仍然是 $r$。把 burst 设成「一分钟的配额」等于没有限流。
- 排队还是拒绝：同步 API 通常返回 429 和 `Retry-After`；内部推理网关可以让可延迟的请求排队，但排队要按租户权重，而不是 FIFO，否则大流量租户会把队列堵死。

并发方面，单机可以用 per-key 锁，或者把 key 哈希到不同 shard；多机把桶放进缓存，用事务把「读、补充、扣款」做成原子操作。不要先 get 再 set，那会丢失更新，和 BankAccount 的竞态是同一种结构。分布式时钟可以用逻辑时间，或者接受略微宽松的结果，强同步时钟不是这一轮的重点。

接到 Grok API 时，计费单位从请求变成 token，框架不用变，只需调整 `cost` 的定义。先把状态和并发约定定清楚，再讨论其他组件；缓存层见 `xai-lru-cache`。

## 追问

**为什么面试官会暗示 lazy refill？**
不用定时器，状态小，单测只需要推进 `now`。热路径上补 token 是 $O(1)$。

**突然来了 10 倍流量怎么办？**
burst 先吃掉尖峰，之后返回 429。公平队列保证小租户仍能拿到 $w_i$ 的份额。不要靠继续调大 burst。

**和推理 batching 是什么关系？**
限流在入口保护 GPU 队列，batching 在内部提高利用率。入口公平不等于 decode 阶段的公平，后者还要看 KV 占用和抢占，见 `xai-grok-moe`。

**固定窗口能过吗？**
计数可以写对，但 window boundaries 处的突发会达到 $2r$。要自己点出这一点，再换成令牌桶。

## 相关题

- [[anthropic-rate-limit]]：和本题共用同一份两层令牌桶程序；Anthropic 那题正文更偏系统设计，讲请求数和 token 数两类配额、滑动窗口和 Redis 故障时 fail closed。
- [[p3a-xai-distributed-token-bucket-limiter]]：同为 xAI 的令牌桶编码题，只有每用户一个桶，重点换成多实例共享限额时补充、检查、扣减怎么原子化。
- [[p3a-xai-rate-limiter-design]]：同为 xAI，从入口限流延伸到出站保护下游配额，中间用有界队列和背压衔接。
